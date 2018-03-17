/**
 * Created by knight on 2017/11/5.
 */
//写cookies
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
    // document.cookie = ""
}

//删除cookies
// function delCookie(name)
// {
//     setCookie(name,"hhhh", -1);
// }
// function setsCookie(name,value,expiredays) {
//     var exdate = new Date()
// 	exdate.setDate(exdate.getDate() + expiredays)
// 	document.cookie = name + "=" + escape(value) + ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString())
// }
// function getCookie(name) {
//     var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
//     if (arr = document.cookie.match(reg)) {
//         return unescape(arr[2]);
//     } else {
//         return null;
//     }
// }



function delCookie(name) {
    var date = new Date();
    date.setTime(date.getTime() - 10000);
    document.cookie = name + "=a; expires=" + date.toGMTString();
}