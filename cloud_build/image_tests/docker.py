from typing import List

arch_map= {"x86_64": 'amd64', "i586": '386', "aarch64": 'arm64', "riscv64": "riscv64", "loongarch64": "loong64"}

def test_docker(image, branch, arch: str) -> List[str]:
    dockerfile = rf"""FROM scratch
ADD {image} /

RUN true > /etc/security/limits.d/50-defaults.conf

CMD ["/bin/bash"]"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)

    docker_arch = arch_map.get(arch)
    if docker_arch is None:
        print(f'not found arch name {arch} for file in map {arch_map}')
        print('this test is skipped')
        return []
                        
    name = f'cloud_build_test_{abs(hash(image))}'
    test_commads = [
        'apt-get update',
        'apt-get dist-upgrade -y',
        'apt-get install -y vim-console',
        '[ -L /var/run ]',
        '[ -L /var/lock ]',
        f'cat /etc/os-release | grep -i {branch}'
    ]

    if branch.lower() == "sisyphus":
        test_commads.append('rpm -qa | grep -i branding | grep -i sisyphus')
    else:
        test_commads.append('rpm -qa | grep -i branding | grep -i container')

    test_commad = " && ".join(test_commads)
    commands = [
        f'podman build --tag={name} --platform=linux/{docker_arch} .',
        f"podman run --rm --platform=linux/{docker_arch} localhost/{name} /bin/sh -c " f"'{test_commad}'",
        f'podman image rm localhost/{name}'
    ]

    return commands
