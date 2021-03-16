() => {
    var timerid = setInterval(frame, 10);
    function frame() {
        let end = document.documentElement.scrollHeight;
        if (document.documentElement.clientHeight == document.documentElement.scrollHeight) {
            // 刚触发 load 事件时，页面也能未加载好， 导致 clientHeight 会等于 scrollHeight
            end = document.documentElement.clientHeight * 3;
        }
        if(document.documentElement.scrollTop + document.documentElement.clientHeight < end) {
            document.documentElement.scrollTop += (1 + Math.round(Math.random()*10)) * 4;
        } else {
            clearInterval(timerid);
            return;
        }
    }
}
