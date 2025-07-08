from flask import Blueprint, jsonify,request
from app.services.post_service import (create_post,edit_post)

# from app.services.post_service import (create_post,edit_post,delete_post,restore_post,re_post,getall_post,userspecific_post)
post_bp=Blueprint('post_bp',__name__)
print("Post blueprint is being loaded...")  # Top of file

@post_bp.route('/post/createpost', methods=['POST'])
def createpost():
    return create_post(request)


@post_bp.route('/post/editpost/<id>',methods=['POST'])
def editpost(id):
    return edit_post(request,id)


# @post_bp('/post/deletepost',methods=['POST'])
# def deletepost():
#     return delete_post(request)


# @post_bp('/post/restorepost',methods=['POST'])
# def restorepost():
#     return restore_post(request)


# @post_bp('/post/repost/<id>',methods=['POST'])
# def repost():
#     return re_post(request,id)


# @post_bp('/post/getallpost',methods=['POST'])
# def getallpost():
#     return getall_post(request)


# @post_bp('/post/userspecificpost/<id>',methods=['POST'])
# def userspecificpost():
#     return userspecific_post(request,id)

