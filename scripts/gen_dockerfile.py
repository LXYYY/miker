import os
import getpass


def gen_str_replace(file, replace):
    str_lists = []
    base_str = None
    with open(file, 'r') as file:
        base_str = file.read()
    if not replace:
        str_lists.append(base_str)
    else:
        for line in replace:
            str = base_str
            for pair in line:
                str = str.replace(pair[0], pair[1])
            str_lists.append(str)
    return str_lists


def gen_text_to_install_ros_package(ros_version, package_list):
    replace = []
    for package_name in package_list:
        replace.append([('<package_name>', package_name)])
    str = []
    str = str + gen_str_replace('contexts/ros-setup.txt',
                                [[('<ros_version>', ros_version)]])
    str = str + gen_str_replace('contexts/ros-packages.txt', replace)
    return str


def gen_text_to_add_user(user_name, password, user_gid='1000'):
    replace = [[('<user_name>', user_name), ('<password>', password),
                ('<user_gid>', '1000'), ('<user_uid>', user_gid)]]
    return gen_str_replace('contexts/add-user.txt', replace)


def gen_text_for_base_image(base_image):
    return ["FROM " + base_image]


def gen_text_and_cmd_for_ssh_config():
    return gen_str_replace('contexts/ssh-config.txt',
                           []), gen_str_replace('cmd/sshd-cmd.txt', [])


def gen_text_to_add_entrypoint(entrypoints):
    copy_str = []
    merged_ep_str = []
    for entrypoint in entrypoints:
        entrypoint_path = os.path.abspath("entrypoints/" + entrypoint)
        if os.path.exists(entrypoint_path):
            copy_str.append("COPY " + entrypoint_path + " /")
            merged_ep_str.append("source /" + entrypoint)
        else:
            print("Entrypoint file not found: " + entrypoint_path)
    return copy_str, merged_ep_str


def main():
    package_list = ["perception", "desktop"]
    cmd = ['/bin/bash']
    merged_entrypoint_str = []
    base_image = ''
    ros_version = ''
    image_name = ''
    image_dir_path = os.path.abspath('dockers')
    cmd_type = ['CMD ["bash"]']

    print("Welcome to Miker Dockerfile generator!")

    while (True):
        image_name = input("Please choose an image name:")
        image_dir_path = os.path.abspath(
            os.path.join(image_dir_path, image_name))
        print(image_dir_path)
        if os.path.exists(image_dir_path):
            print("  Image already exists: " + image_name)
            continue
        else:
            break

    print("Please choose a base image:")

    base_image_list = [
        'ubuntu:20.04', 'ubuntu:18.04', 'ubuntu:16.04', 'ubuntu:14.04',
        'others'
    ]
    ros_version_list = ['noetic', 'melodic', 'kinetic', 'indigo']
    base_image_opt_str = ''
    for i, base_image in enumerate(base_image_list):
        base_image_opt_str += '  {} - {}\n'.format(i + 1, base_image)
    base_image_n = input(base_image_opt_str)
    base_image = base_image_list[int(base_image_n) - 1]

    if base_image == 'others':
        base_image = input('  input your base image:')
        ros_version = input('  input your ros version:')
    else:
        base_image = base_image_list[int(base_image_n) - 1]
        ros_version = ros_version_list[int(base_image_n) - 1]
    print("ROS Version: " + ros_version)
    str_lists = gen_text_for_base_image(base_image)

    print("Please choose ROS packages:")
    package_list = input(
        "  input your package list, leave empty if you don't want ROS to install:"
    ).split(',')
    if package_list:
        str_lists = str_lists + gen_text_to_install_ros_package(
            ros_version, package_list)

    print("Please create your user:")
    user_name = input('  input your user name:')
    password = ''
    while (True):
        password = getpass.getpass('  input your password:')
        password_rp = getpass.getpass('  input your password again:')
        if password == password_rp:
            break

    str_lists = str_lists + gen_text_to_add_user(user_name, password)

    # if config sshd
    if_sshd = input('Do you want to config sshd? (y/N)')
    if if_sshd == 'y':
        [ssh_config_str, sshd_cmd] = gen_text_and_cmd_for_ssh_config()
        cmd_type.append('sshd')
        cmd = cmd + (sshd_cmd)
        str_lists = str_lists + ssh_config_str

    # config entrypoint
    copy_entrypoint_str, merged_entrypoint_str = gen_text_to_add_entrypoint(
        ['ros_entrypoint.sh'])

    str_lists = str_lists + copy_entrypoint_str

    str_lists.append('COPY entrypoint.sh /\n')
    str_lists.append('ENTRYPOINT [ "/entrypoint.sh" ]\n')

    print("Please choose CMD:")
    cmd_opt_str = ''
    for cmd_t in cmd_type:
        cmd_opt_str += '  {} - {}\n'.format(cmd_type.index(cmd_t) + 1, cmd_t)
    cmd_n = input(cmd_opt_str)
    str_lists.append(cmd[int(cmd_n) - 1])

    print(str_lists)

    os.mkdir(image_dir_path)

    dockerfile = open(os.path.join(image_dir_path, 'Dockerfile'), 'w')
    for str in str_lists:
        dockerfile.write(str + '\n\n')
    dockerfile.close()

    entrypoint_file = open(os.path.join(image_dir_path, 'entrypoints.sh'), 'w')
    for entrypoint in merged_entrypoint_str:
        entrypoint_file.write(entrypoint + '\n')
    entrypoint_file.close()


if __name__ == "__main__":
    main()
