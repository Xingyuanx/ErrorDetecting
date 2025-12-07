// var srverUrl = window.UPLOAD_URL
/*参数说明：
        * srcHref 文件地址
        * imgUrl 主图片地址
        * text 标题
        * */
function addCode(srcHref, imgUrl) {
  var textNane = ''
  if (imgUrl === '' || imgUrl === null) {
    // img = 'style="background-image: url(' + srverUrl + '/fonts/img.png);"'
    img = 'style="background-image: none;"'
    var textNane = srcHref
  } else {
    img = 'style="background-image: url(./FileS/' + srcHref + '/preview/' + imgUrl + ');"'
  }

  var code = $('<div class="col-sm-6 col-md-2">' +
    '<div data-leaves="' + srcHref + '" class="thumbnail move">' +
    '<div class="thumbnail disBottom">' +
    '<div id="addHeight" ' + img + ' >' + textNane +
    '</div>' +
    '<div class="caption">' +
    '<p class="title">' + srcHref + '</p>' +
    '</div>' +
    '</div>' +
    '</div>' +
    '</div>');
  $('.fusioncool-html-files-switch').append(code);

}
let xhr = new XMLHttpRequest()
xhr.onreadystatechange = function () {
  if (xhr.readyState === 4 && xhr.status === 200) {
    var dataS = xhr.response
    // console.log(dataS)
    var mydata = JSON.parse(dataS).data.floder;   //JSON.parse() 方法用于将一个 JSON 字符串转换为对象。
    var imgUrl = JSON.parse(dataS).data.imgUrl;   //JSON.parse() 方法用于将一个 JSON 字符串转换为对象。
    var dataLength = mydata.length;
    for (i = 0; i < dataLength; i++) {
      addCode(mydata[i].title, imgUrl[i]);
    }
  }
}
xhr.open('get', '/item')
xhr.send()

setTimeout(function () {
  $(".move").on('click', function () {
    var addUrl = $(this).attr("data-leaves");
    // $('.bntClass').show();
    var shareUrl = "/FileS/" + addUrl;
    // console.log(shareUrl)
    window.location.href = shareUrl;      //跳转事件
    //分享按钮事件
    $('#share').click(function () {
      //    console.log($('textarea'))
      $("#input").val(shareUrl).select();  // 修改文本框的内容 选中文本
      document.execCommand("copy"); // 执行浏览器复制命令
      $('#share').html("复制成功");
      $('#share').css("background-color", "#31c56a");
      setTimeout(function () {
        $('#share').empty();
        $('#share').append('<span class="glyphicon glyphicon-share-alt" style="top: 2px;"></span>')
        $('#share').css("background-color", "#0c85f1");
      }, 1500)
    })
  });
  $("#goBack").on('click', function () {
    $('#windWeb').remove()
    $('.bntClass').hide()
  });
}, 300)
var mo=function(e){e.preventDefault();};
function stop() {
  document.body.style.overflow = 'hidden';
  document.addEventListener("touchmove", mo, false);//禁止页面滑动
}
function move() {
  document.body.style.overflow = '';//出现滚动条
  document.removeEventListener("touchmove", mo, false);
}
// console.log(document.body.clientWidth)

$("#switch").click(function () {
  console.log($(".user").css('left'))
  if ($(".user").css('left') < '0') {　　//如果.user是隐藏的则显示node元素，否则隐藏
    $(".user").css('left','0')
    stop()
  } else {
    $(".user").css('left','');
    move()
  }
});

