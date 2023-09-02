# درباره موآ


موآ یک [موتور فراجستجو] آزاد، بر پایه SearXNG
 است که نتایج دیگر {{link('موتور جستجوها', 'preferences')}} را جمع می کند در حالی که اطلاعاتی از شما ذخیره نمی‌کند.

پروژه SearXNG توسط یک جامعه باز هدایت می شود، می‌توانید در ماستودون به ما بپیوندید
اگر سوالی دارید یا می‌خواهید به ما بپیوندید می‌توانید اینجا [ماستودون] موآ را ببینید.

- می توانید ترجمه های SearXNG را در [وب سایت] بهبود بخشید و به موآ نیز کمک کنید.
- توسعه را ردیابی کنید، مشارکت ها را ارسال کنید و مشکلات را در [کد منبع موآ] گزارش کنید.
- برای دریافت اطلاعات بیشتر، از مستندات پروژه SearXNG در [اسناد SearXNG] استفاده کنید.

## چرا از موآ استفاده کنید؟

- ممکن است موآ به اندازه گوگل‌ نتایج شخصی سازی شده را به شما ارائه ندهد، اما اطلاعات شما را ردیابی نمی‌کند.
- موآ به آنچه شما جستجو می کنید اهمیتی نمی دهد، هرگز چیزی را با افراد شخص ثالث به اشتراک نمی گذارد
   ، و نمی توان از آن برای به خطر انداختن شما استفاده کرد.
- موآ نرم افزار آزاد است، کد 100٪ باز است و همه می‌توانند به توسعه ان کمک کنند

اگر به حریم خصوصی اهمیت می دهید، می خواهید یک کاربر آگاه باشید، یا می‌خواهید در آزادی دیجیتال باشید،
 موآ را موتور جستجوی پیش فرض خود قرار دهید یا آن را بر روی سرور خود اجرا کنید

## چگونه موآ را به عنوان موتور جستجوی پیش فرض تنظیم کنم؟

موآ از [OpenSearch] پشتیبانی می کند. برای اطلاعات بیشتر در مورد تغییر موتور جستجو پیش فرض خود
، مستندات مرورگر خود را ببینید:

- [Firefox]
- [Microsoft Edge] - در پشت پیوند، دستورالعمل های مفیدی نیز خواهید یافت
   برای کروم و سافاری
- مرورگرهای مبتنی بر [Chromium] فقط وب سایت هایی را اضافه می کنند که کاربر بدون مسیر به آنها پیمایش می کند.

هنگام اضافه کردن یک موتور جستجو، نباید تکراری با همان نام وجود داشته باشد. اگر
شما با مشکلی روبرو می شوید که نمی توانید موتور جستجو را اضافه کنید، می توانید یکی از موارد زیر را انجام دهید:

- حذف تکراری (نام پیش فرض: موآ) یا
- با مالک تماس بگیرید تا نمونه را نامی متفاوت از پیش فرض قرار دهد.

## چگونه کار می کند؟

موآ یک انشعاب از SearXNG است و خود آن نیز بر پایه [searx] [موتور فراجستجو] که تلاش می‌کرد
با الهام از [پروژه Seeks] حریم خصوصی را برای شما فراهم کند.

موآ نتیجه جستجوی شما را از موتور جستجو های مختلف جمع آوری می‌کند و در دسترس شما قرار می‌دهد.
حتی می‌توانید موتور های مورد نیازتان رو خودتان انتخاب کنید! آمار موتورهای مورد استفاده : {{link('صفحه آمار', 'stats')}}

## چگونه می توانم خودم موآ را داشته باشم؟
می‌توانید
[کد منبع موآ] دریافت کنید و خودتان آن را اجرا کنید!

نمونه خود را به این [لیست عمومی اضافه کنید
instances]({{get_setting('brand.public_instances')}}) برای کمک به افراد دیگر
حفظ حریم خصوصی و آزادتر کردن اینترنت. هر چه اینترنت غیرمتمرکزتر باشد
، آزادی بیشتر است!


[کد منبع موآ]: {{GIT_URL}}
[ماستودون]: https://mastodon.world/@moa_engine/
[اسناد SearXNG]: {{get_setting('brand.docs_url')}}
[searx]: https://github.com/searx/searx
[موتور فراجستجو]: https://fa.wikipedia.org/wiki/Metasearch_engine
[وب سایت]: https://translate.codeberg.org/projects/searxng/
[پروژه Seeks]: https://beniz.github.io/seeks/
[OpenSearch]: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
[Firefox]: https://support.mozilla.org/en-US/kb/add-or-remove-search-engine-firefox
[Microsoft Edge]: https://support.microsoft.com/en-us/help/4028574/microsoft-edge-change-the-default-search-engine
[Chromium]: https://www.chromium.org/tab-to-search