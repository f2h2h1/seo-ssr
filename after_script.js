() => {
    let delArr = [];
    let scriptTag = document.evaluate('//script', document);
    for (let d = scriptTag.iterateNext(); d != null; d = scriptTag.iterateNext()) {
        if (d.src) {
            if (d.src.search(/\/assets\/js\/(?:(.*)).js/i) > 0) {
                delArr.push(d);
            }
        }
    }
    let linkTag = document.evaluate('//link', document);
    for (let d = linkTag.iterateNext(); d != null; d = linkTag.iterateNext()) {
        if (d.href) {
            if (d.href.search(/\/assets\/js\/(?:(.*)).js/i) > 0) {
                delArr.push(d);
            }
            if (d.href.search(/\/assets\/css\/(?:(.*)).css/i) > 0 && d.rel && d.rel == 'prefetch') {
                delArr.push(d);
                continue;
            }
        }
    }
    let noscript = document.evaluate('//noscript', document); // 删掉 noscript 标签
    for (let d = noscript.iterateNext(); d != null; d = noscript.iterateNext()) {
        delArr.push(d);
    }
    for (let i = 0; i < delArr.length; i++) {
        delArr[i].parentNode.removeChild(delArr[i]);
    }
    return document.documentElement.outerHTML;
}
