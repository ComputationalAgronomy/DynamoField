
aws dynamodb list-tables --endpoint-url http://localhost:8000

aws --endpoint-url http://localhost:8000 dynamodb create-table \
--table-name ft_db \
--attribute-definitions AttributeName=FT_ID,AttributeType=S AttributeName=meta,AttributeType=S \
--key-schema AttributeName=FT_ID,KeyType=HASH AttributeName=meta,KeyType=RANGE \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 


aws --endpoint-url http://localhost:8000