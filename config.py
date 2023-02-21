class Config :
    HOST = 'yh-db.cy1i4s2uewlm.ap-northeast-2.rds.amazonaws.com'
    DATABASE = 'memo_db3'
    DB_USER = 'memo_db_user'
    DB_PASSWORD = 'yh1234db'
    SALT = 'dskj29jcdn12jn'

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = 'yhacdemy20230105##hello'
    JWT_ACCESS_TOKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True

    # AWS 관련 키
    ACCESS_KEY = 'AKIAYYISOLC4P753LEX7'
    SECRET_ACCESS = '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'
    
    # S3 버킷
    S3_BUCKET = 'hyunsungkr-yh-test'
    # S3 Location
    S3_LOCATION = 'https://hyunsungkr-yh-test.s3.ap-northeast-2.amazonaws.com/'