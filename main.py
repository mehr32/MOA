from concurrent.futures import ThreadPoolExecutor
from core.engine_loader import EngineLoader
from core.plugin_loader import PluginLoader
import logging
from fastapi import FastAPI, Query
from typing import Optional
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from fastapi import HTTPException

# Start logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Loading the engines and plugins
ploader = PluginLoader()
loader = EngineLoader()
engine_status = loader.list_engines()
plugin_status = ploader.list_plugins()

# Show engines in each category
for types in engine_status:
    logger.info(f"{types} Engines: %s", engine_status[types])

# Show healthy and faulty plugins
logger.info("Active Plugins: %s", plugin_status["active"])
logger.warning("Failed Plugins: %s", plugin_status["failed"])


app = FastAPI()
@app.get("/search")

async def search(
    q: Optional[str] = Query(None, description="Search query"),
    engine: Optional[list[str]] = Query(None, description="search engine names default = all"),
    plugin: Optional[list[str]] = Query(None, description="search engine names default = all"),
    time_range: Optional[str] = Query("", description="Time range filter"),
    lang: Optional[str] = Query("", description="search language "),
    size: Optional[int] = Query(None, description="Number of results per engine default all results"),
    page: int = Query(1, description="Page number"),
    safesearch: int = Query(0, description="Safe search level"),
    country: str = Query("", description="Country to search"),
    category: str = Query("general", description=""),
    api_mode: str = Query("normal", description="API behavior. stream or normal"),
    ):
    # Send error if input query is missing
    if not q:
        raise HTTPException(status_code=400, detail="Search query input cannot be empty.")


    category = category.lower() if category else "general"
    if category not in engine_status:
        category = "general"

    if engine:
        if category in engine_status:
            invalid_engines = [e for e in engine if e not in engine_status[category]]
            if invalid_engines:
                return {
                    "error": f"Engine(s) {invalid_engines} not found in category '{category}'"
                }
        selected_engines = engine
    else:
        # If no engine is given, use category
        selected_engines = engine_status[category]

    # Determining and validating pre and post plugins
    selected_pre_plugins = []
    selected_post_plugins = []

    if plugin:
        for plugin_name in plugin:
            plugin_instance = ploader.get_plugin(plugin_name)
            if not plugin_instance:
                logger.warning("Plugin '%s' not found or failed to load.", plugin_name)
                continue

            plugin_type = plugin_instance.get_type().lower()
            if plugin_type == "pre":
                selected_pre_plugins.append(plugin_instance)
            elif plugin_type == "post":
                selected_post_plugins.append(plugin_instance)
            else:
                logger.warning("Plugin '%s' has unknown type '%s'", plugin_name, plugin_type)
    else:
        selected_pre_plugins = ploader.pre_plugins
        selected_post_plugins = ploader.post_plugins

    # Creating search parameters
    search_params = {
        "query": q,
        "page": page,
        "safesearch": safesearch,
        "time_range": time_range,
        "num_results": size, # For engines that can return a certain number of results by default
        "locale": lang,
        "country": country
    }

    # Normal api mode takes all results from all engines. Then sends them all at once.
    if api_mode == "normal":

        results = {}
        pre_plugin_outputs = {} # Pre plugins also work in parallel with engines.

        with ThreadPoolExecutor() as executor:
            futures = {}
            for engine_name in selected_engines:
                engine_instance = loader.get_engine(engine_name)
                if not engine_instance:
                    logger.error("Engine %s not found!", engine_name)
                    continue

                futures[executor.submit(engine_instance.search, **search_params)] = ("engine", engine_name)

            for plugin in selected_pre_plugins:
                futures[executor.submit(plugin.run, q)] = ("pre_plugin", plugin.__class__.__name__)

            for future in futures:
                ftype, name = futures[future]
                try:
                    output = future.result()
                    if ftype == "engine":
                        if size and isinstance(output, dict) and "results" in output and isinstance(output["results"], list):
                            output["results"] = output["results"][:size]
                        results[name] = output
                    elif ftype == "pre_plugin":
                        pre_plugin_outputs[name] = output
                except Exception as e:
                    logger.error("%s %s failed: %s", ftype.capitalize(), name, str(e))
                    if ftype == "engine":
                        results[name] = {"error": str(e)}
                    elif ftype == "pre_plugin":
                        pre_plugin_outputs[name] = {"error": str(e)}

        return {
            "results": results,
            "pre_plugins": pre_plugin_outputs
        }

    """
    In streaming API mode, the results of engines and pre-plugins are executed in parallel and sent separately to the client without delay.
    """
    elif api_mode == "stream":
        async def event_stream():
            queue = asyncio.Queue()

            async def run_tasks():
                tasks = []

                for eng_name in selected_engines:
                    engine_instance = loader.get_engine(eng_name)
                    if not engine_instance:
                        await queue.put({"type": "engine_result", "name": eng_name, "error": "Engine not found"})
                        continue

                    async def run_engine(name, instance):
                        try:
                            result = await asyncio.to_thread(
                                instance.search, **search_params)
                            if size and isinstance(result, dict) and "results" in result:
                                result["results"] = result["results"][:size]
                            await queue.put({"type": "engine_result", "name": name, "result": result})
                        except Exception as e:
                            await queue.put({"type": "engine_result", "name": name, "error": str(e)})

                    tasks.append(run_engine(eng_name, engine_instance))

                for pre_plugin in selected_pre_plugins:
                    plugin_name = pre_plugin.__class__.__name__

                    async def run_pre_plugin(instance, name):
                        try:
                            result = await asyncio.to_thread(instance.run, q)
                            await queue.put({"type": "pre_plugin_result", "name": name, "result": result})
                        except Exception as e:
                            await queue.put({"type": "pre_plugin_result", "name": name, "error": str(e)})

                    tasks.append(run_pre_plugin(pre_plugin, plugin_name))

                await asyncio.gather(*tasks)

                for post_plugin in selected_post_plugins:
                    plugin_name = post_plugin.__class__.__name__
                    try:
                        result = await asyncio.to_thread(post_plugin.run, q)
                        await queue.put({"type": "post_plugin_result", "name": plugin_name, "result": result})
                    except Exception as e:
                        await queue.put({"type": "post_plugin_result", "name": plugin_name, "error": str(e)})

                await queue.put({"type": "done", "data": "[DONE]"})

            asyncio.create_task(run_tasks())

            while True:
                data = await queue.get()
                if data.get("type") == "done":
                    yield json.dumps(data).encode() + b"\n"
                    break
                yield json.dumps(data).encode() + b"\n"

        return StreamingResponse(event_stream(), media_type="application/json")

    else:
        return "api_mode should be normal or stream."

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add route for favicon.ico
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

