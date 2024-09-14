import argparse

import docker
import json
from docker.errors import APIError
import base64
import os


def load_mirrors(content):
    data = json.load(content)
    return data.get('hub-mirror', [])


def authenticate(docker_client, username, password, repository):
    auth_config = docker_client.login(
        username=username,
        password=password,
        repository=repository,
        reauth=True  # 重新授权，如果之前已经登录
    )
    # 登录后，docker-py会自动处理后续的RegistryAuth
    return auth_config


def pull_retag_push(docker_client, source, target, auth_str=None):
    try:
        # 拉取镜像
        print(f"Pulling {source}...")
        docker_client.images.pull(source)

        # 重新打标签
        print(f"Tagging {source} as {target}...")
        docker_client.images.tag(source, target)

        # 推送镜像
        print(f"Pushing {target}...")
        for line in docker_client.images.push(target, stream=True, auth=auth_str if auth_str else None, decode=True):
            print(json.dumps(line, indent=2))
    except APIError as e:
        print(f"Error processing {source}: {e}")


def main(content, username, password, repository):

    docker_client = docker.from_env()

    # 加载镜像列表
    mirrors = load_mirrors(content)

    # 认证（如果需要）
    if username and password:
        auth_config = authenticate(docker_client, username, password, repository)
        # 将认证信息转换为base64字符串（尽管docker-py通常会自动处理）
        # 但如果我们需要手动传递它（例如，在某些Docker API调用中），可以这样做
        # 注意：这里的auth_str实际上在push时可能不需要，因为docker-py会处理它
    #     auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
    # else:
    #     auth_str = None

    # 处理每个镜像
    for mirror in mirrors:
        if not mirror:
            continue

        # 构建目标镜像名
        if not repository:
            target = f"{username}/{mirror.replace('/', '.')}"
        else:
            target = f"{repository}/{mirror.replace('/', '.')}"

        # 执行拉取、重新打标签和推送操作
        pull_retag_push(docker_client, mirror, target, auth_config)
        # pull_retag_push(docker_client, mirror, target, auth_str)


if __name__ == "__main__":
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description='My Python script')

    # 添加参数
    parser.add_argument('--username', type=str, required=True, help='Username')
    parser.add_argument('--password', type=str, required=True, help='Password')
    parser.add_argument('--repository', type=str, required=True, help='Repository')
    parser.add_argument('--content', type=str, required=True, help='content')

    # 解析参数
    args = parser.parse_args()
    main(args.content, args.username, args.password, args.repository)
