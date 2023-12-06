$(function (){
    $('.pay').click(function () {
        let goods_id = $(this).attr('goods_id')
        $.ajax({
            url:'/pay/',
            type:'post',
            data: {'goods_id':goods_id},
            success:function (args) {
                if (args.code === 1000) {
                    window.location.reload()
                    alert(args.msg)
                }
                else {
                    alert(args.msg)
                }
            }
        })
    })
})


$(function (){
    $('.cancel').click(function () {
        let goods_id = $(this).attr('goods_id')
        $.ajax({
            url:'/cancel/',
            type:'post',
            data: {'goods_id':goods_id},
            success:function (args) {
                window.location.reload()
                alert(args.msg)
            }
        })
    })
})


$(function (){
    $("#set_password").click(function () {
        $.ajax({
            url:'/set_password/',
            type:'post',
            data: {'old_password':$('#id_old_password').val(), 'password':$('#id_new_password').val(), 'confirm_password':$('#id_confirm_password').val()},
            success:function (args) {
                if (args.code===1000) {
                    alert(args.msg)
                    window.location.reload()
                }
                else {
                    if (args.code === 1001) {
                        $.each(args.msg,function (index,obj) {
                            $("#password_error").text(obj[0])
                        })
                    }
                    else {
                        $("#password_error").text(args.msg)
                    }
                }
            }
        })
	})
})


$(function (){
    $("#avatar").change(function () {
        let myFileReaderObj = new FileReader();
        let fileObj = $(this)[0].files[0];
        myFileReaderObj.readAsDataURL(fileObj)
        myFileReaderObj.onload = function () {
            $('#myimg').attr('src', myFileReaderObj.result)
        }
    })
})


$(function (){
    $("#set_avatar").click(function () {
        let formDateObj = new FormData();
        formDateObj.append('avatar',$('#avatar')[0].files[0]);
        $.ajax({
            url:'/set_avatar/',
            type:'post',
            data:formDateObj,
            contentType:false,
            processData:false,
            success:function (args) {
                if (args.code === 1000) {
                    alert(args.msg)
                    window.location.reload()
                }
            }
        })
    })
})


function test() {
	let inputEle = document.getElementById("search");
	let search = inputEle.value;
	if(search){
		alert("不  给  搜  索")
	}
	else{
		alert("关键字不能为空!")
	}
}