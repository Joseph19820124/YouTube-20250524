# AWS Lambda Deployment Guide

## 📋 概述

这个Lambda function用于：
1. 接收YouTube频道ID作为输入
2. 获取该频道的所有视频ID
3. 批量向SRT API发送请求处理每个视频

## 🚀 部署步骤

### 1. 准备部署包

```bash
# 创建部署目录
mkdir lambda_deployment
cd lambda_deployment

# 复制必要文件
cp ../lambda_youtube_srt.py ./
cp ../youtube_video_fetcher.py ./
cp ../lambda_requirements.txt ./requirements.txt

# 安装依赖
pip install -r requirements.txt -t .

# 创建部署包
zip -r youtube_srt_lambda.zip .
```

### 2. 在AWS Console创建Lambda函数

1. 登录AWS Console，进入Lambda服务
2. 点击"创建函数"
3. 选择"从头开始创建"
4. 函数名称: `youtube-srt-processor`
5. 运行时: `Python 3.9` 或 `Python 3.11`
6. 架构: `x86_64`
7. 执行角色: 创建具有基本Lambda权限的新角色

### 3. 上传代码

1. 在函数配置页面，选择"上传来源" -> "上传 .zip 文件"
2. 上传刚才创建的 `youtube_srt_lambda.zip`
3. 处理程序设置为: `lambda_youtube_srt.lambda_handler`

### 4. 配置环境变量

在"配置"标签页的"环境变量"中添加：
- `YOUTUBE_API_KEY`: 你的YouTube Data API密钥

### 5. 调整超时设置

- 在"配置" -> "常规配置"中
- 将超时时间设置为 `15分钟` (根据频道视频数量调整)
- 内存设置为 `512MB` 或更高

## 📝 输入格式

Lambda function期望的输入JSON格式：

```json
{
  "channel_id": "UCuDdJRJ6qR-wGILbpq-FXCw",
  "max_videos": null,
  "delay": 1.0,
  "fetch_only": false
}
```

### 参数说明

- `channel_id` (必需): YouTube频道ID
- `max_videos` (可选): 限制处理的视频数量，null表示处理所有视频
- `delay` (可选): 请求间隔秒数，默认1.0秒
- `fetch_only` (可选): 是否只获取不处理，默认false

## 📤 输出格式

成功响应格式：

```json
{
  "statusCode": 200,
  "body": {
    "channel_id": "UCuDdJRJ6qR-wGILbpq-FXCw",
    "total_videos": 150,
    "success_count": 145,
    "fail_count": 5,
    "success_rate": "96.7%",
    "processing_time": 245000,
    "results": [
      {
        "index": 1,
        "video_id": "video123",
        "title": "视频标题",
        "published_at": "2024-01-01T10:00:00Z",
        "srt_request": {
          "success": true,
          "data": {...},
          "status_code": 200
        }
      }
    ],
    "summary": {
      "latest_video": {...},
      "oldest_video": {...}
    }
  }
}
```

## 🧪 测试

### 使用AWS Console测试

1. 在Lambda函数页面点击"测试"
2. 创建新的测试事件，使用上面的输入格式
3. 点击"测试"按钮执行

### 使用AWS CLI测试

```bash
aws lambda invoke \
    --function-name youtube-srt-processor \
    --payload '{"channel_id":"UCuDdJRJ6qR-wGILbpq-FXCw","max_videos":5}' \
    response.json
```

### 本地测试

```bash
# 设置环境变量
export YOUTUBE_API_KEY="your_api_key_here"

# 运行本地测试
python lambda_youtube_srt.py
```

## ⚠️ 注意事项

1. **API限制**: YouTube Data API有配额限制，请合理设置请求频率
2. **超时设置**: 处理大量视频时需要足够的超时时间
3. **错误处理**: 函数会继续处理即使某些视频请求失败
4. **内存使用**: 大量视频数据可能需要更多内存
5. **日志监控**: 查看CloudWatch日志了解执行详情

## 🔧 故障排除

### 常见错误

1. **API Key错误**: 检查环境变量YOUTUBE_API_KEY是否正确设置
2. **超时错误**: 增加Lambda超时时间或减少max_videos参数
3. **内存不足**: 增加Lambda内存配置
4. **网络错误**: 检查Lambda函数的VPC配置

### 日志查看

在CloudWatch Logs中查看详细执行日志：
`/aws/lambda/youtube-srt-processor`

## 🚀 进阶功能

### 与其他AWS服务集成

1. **API Gateway**: 创建REST API端点
2. **SQS**: 异步处理大量请求
3. **S3**: 存储处理结果
4. **EventBridge**: 定时触发处理

### API Gateway集成示例

```bash
# 创建API Gateway触发器
aws apigatewayv2 create-api \
    --name youtube-srt-api \
    --protocol-type HTTP \
    --target arn:aws:lambda:region:account:function:youtube-srt-processor
```

## 📞 支持

如遇问题，请检查：
1. CloudWatch日志
2. 环境变量配置
3. 网络连接
4. API配额使用情况
