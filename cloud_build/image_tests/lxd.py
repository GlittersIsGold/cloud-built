from typing import List


def test_lxd(image, branch, arch: str) -> List[str]:
    test_commads = [
       'apt-get update',
       'apt-get install -y vim-console',
       f'cat /etc/os-release | grep -i {branch}',
       'rpm -qa | grep -i branding | grep -i container',
       'systemctl list-units --failed | grep -i 0'
    ]

    test_commad = " && ".join(test_commads)
    commands = [
       f'gen-lxd-metadata.sh --name altlinux --description Altlinux --architecture x86_64 --template-hosts ./meta.tar.xz',
       'mkdir rootfs',
       f'tar -xf {image} --directory ./rootfs',
       'distrobuilder pack-lxc /usr/share/doc/distrobuilder-$(rpm -qa --qf "%{VERSION}" distrobuilder)/doc/ci/alt.yaml' + f'./rootfs/ -o image.release={branch} -o image.architecture={arch}',
       f"lxc image import ./meta.tar.xz ./rootfs.tar.xz --alias alt-test",
       f'lxc launch alt-test alt-cont',
       f'lxc-wait --name=alt-cont --state=RUNNING',
       f'lxc exec alt-cont -- {test_commad}',
       f'lxc delete --force alt-cont',
       f'lxc image delete alt-test'
    ]
    return commands
