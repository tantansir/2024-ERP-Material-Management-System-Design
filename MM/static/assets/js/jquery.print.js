(function($) {
    var opt;

    $.fn.jqprint = function(options) {
        // 合并用户传入的选项和默认选项
        opt = $.extend({}, $.fn.jqprint.defaults, options);

        var $element = (this instanceof jQuery) ? this : $(this);

        // 检测是否为 Opera 浏览器
        var isOpera = !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

        if (opt.operaSupport && isOpera) {
            // 如果是 Opera 浏览器，使用新窗口方式
            var tab = window.open("", "jqPrint-preview");
            tab.document.open();
            var doc = tab.document;
        } else {
            // 否则创建一个隐藏的 iframe 用于打印
            var $iframe = $("<iframe />").css({
                position: "absolute",
                width: "0px",
                height: "0px",
                left: "-9999px",
                top: "-9999px"
            }).appendTo("body");

            var doc = $iframe[0].contentWindow.document;
        }

        // 如果选择导入 CSS 样式
        if (opt.importCSS) {
            // 如果存在 print 媒体类型的 CSS 文件，则导入这些文件
            if ($("link[media=print]").length > 0) {
                $("link[media=print]").each(function() {
                    doc.write("<link type='text/css' rel='stylesheet' href='" + $(this).attr("href") + "' media='print' />");
                });
            } else {
                // 否则导入所有的 CSS 文件
                $("link").each(function() {
                    doc.write("<link type='text/css' rel='stylesheet' href='" + $(this).attr("href") + "' />");
                });
            }
        }

        // 是否包含容器
        if (opt.printContainer) {
            doc.write($element.prop('outerHTML'));
        } else {
            $element.each(function() {
                doc.write($(this).html());
            });
        }

        doc.close();

        var printWindow = isOpera ? tab : $iframe[0].contentWindow;
        printWindow.focus();

        // 打印后关闭新窗口（如果是 Opera 浏览器）
        setTimeout(function() {
            printWindow.print();
            if (tab) { tab.close(); }
        }, 1000);
    };

    // 默认选项
    $.fn.jqprint.defaults = {
        debug: false,
        importCSS: true,
        printContainer: true,
        operaSupport: true
    };

    // 获取元素的外部 HTML 内容
    jQuery.fn.outer = function() {
        return $($('<div></div>').html(this.clone())).html();
    };
})(jQuery);
