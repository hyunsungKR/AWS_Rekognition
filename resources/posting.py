from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from mysql.connector import Error
from mysql_connection import get_connection
from datetime import datetime
import boto3
from config import Config

class PostingResource(Resource) :

    def post(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # form-data
        # photo : file
        # content : text

        # 사진과 내용은 필수항목이다!!
        if 'photo' not in request.files or 'content' not in request.form :
            return {'error':'데이터를 정확히 보내세요.'},400
        
        file=request.files['photo']
        content=request.form['content']

        # 내가 한 방법
        # if file.content_type.split('/')[0] != 'image' :
        #     return {'error':'사진만 올려주세요'},400
        
        # 교수님이 한 방법
        if 'image' not in file.content_type :
            return {'error':'이미지 파일만 올려주세요'},400

        print(file.content_type)

        # 2. 사진을 먼저 S3에 저장한다.

        # 파일명을 유니크하게 만드는 방법
        current_time=datetime.now()
        new_file_name=current_time.isoformat().replace(':','_') + file.content_type.split('/')[-1]

        print(new_file_name)

        # 파일명을, 유니크한 이름으로 변경한다.
        # 클라이언트에서 보낸 파일명을 대체!

        file.filename = new_file_name

        # S3에 파일을 업로드하면 된다.
        # S3에 파일 업로드하는 라이브러리가 필요
        # boto3 라이브러리를 이용해서 업로드한다.
        # 참고 : 라이브러리 설치는 pip install boto3

        client=boto3.client('s3',
                    aws_access_key_id = Config.ACCESS_KEY ,
                    aws_secret_access_key = Config.SECRET_ACCESS)
        
        try :
            client.upload_fileobj(file,Config.S3_BUCKET,new_file_name,
                                    ExtraArgs ={'ACL':'public-read','ContentType':file.content_type})
        
        except Exception as e :
            return {'error':str(e)}, 500

        #3. 저장된 사진의 imgUrl을 만든다.
        imgUrl = Config.S3_LOCATION+new_file_name
        # 4. DB에 저장한다.
        try :
            connection = get_connection()
            query='''insert into
                    posting
                    (content,imgUrl)
                    values
                    (%s,%s);'''
            record = (content,imgUrl)
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)},500
        
        return {'result':'success'},200

