function judge() {
	alert("暂  时  缺  货")
}

function test() {
	$(function (){
        let formDateObj = new FormData();
        $.each($('#w').serializeArray(),function (index, obj) {
            formDateObj.append(obj.name, obj.value)
        })
        $.ajax({
            url:'',
            type:'post',
            data:formDateObj,
            contentType:false,
            processData:false,
            success:function (args) {
                if (args.code === 1000) {
                    let confirm_password = prompt("再次确认账号密码")
                    if (confirm_password) {
                        if (confirm_password === args.password) {
                            $('.span3').text('\xa0')
                            setTimeout(function () {alert(args.msg)},400)
                            setTimeout(function () {window.location.href = args.url},600)
                        }
                        else {
                            $('.span3').text("两次输入的账号密码不一致!")
                        }
                    }
                    else {
                        $('.span3').text("账号密码不能为空!")
                    }
                }
                else {
                    if (args.code === 1001) {
                        $('.span3').text(args.msg)
                    }
                    else {
                        $.each(args.msg,function (index,obj) {
                            $('.span3').text(obj[0])
                        })
                    }
                }
            }
        })
	})
}


$(function (){
    $('#id_password').focus(function () {
        $('.span3').text('\xa0')
    })
})