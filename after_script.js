() => {
    let scriptTagArr = [];
    let scriptTag = document.evaluate('//script', document);
    for (let d = scriptTag.iterateNext(); d != null; d = scriptTag.iterateNext()) {
        if (d.src) {
            if (d.src.search(/\/assets\/js\/(?:(.*)).js/i) > 0) {
                scriptTagArr.push(d);
            }
        }
    }
    let linkTag = document.evaluate('//link', document);
    for (let d = linkTag.iterateNext(); d != null; d = linkTag.iterateNext()) {
        if (d.href) {
            if (d.href.search(/\/assets\/js\/(?:(.*)).js/i) > 0) {
                scriptTagArr.push(d);
            }
            if (d.href.search(/\/assets\/css\/(?:(.*)).css/i) > 0 && d.rel && d.rel == 'prefetch') {
                scriptTagArr.push(d);
                continue;
            }
        }
    }
    for (let i = 0; i < scriptTagArr.length; i++) {
        scriptTagArr[i].parentNode.removeChild(scriptTagArr[i]);
    }
    return document.documentElement.outerHTML;
}
