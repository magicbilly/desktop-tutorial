import shutil
import sys
import os


def help_mode():
    """
        显示帮助信息，描述每个模式的功能和用法。
        """
    help_text = """
        Usage: python script.py <mode> <arguments>

        Modes:
        -a: Replace all occurrences of old_part with new_part in filenames.
        -e: Replace the file extension with new_part.
        -p: Replace old_part with new_part in the filename prefix.
        -d: Delete all occurrences of delete_part in filenames.
        -dm: Delete part of the filename between start and end.
        -h: Show this help message.

        Examples:
        1. Replace all occurrences of "old" with "new" in filenames:
           python script.py -a old new
        2. Replace the file extension with "txt":
           python script.py -e txt
        3. Replace "old" with "new" in the filename prefix:
           python script.py -p old new
        4. Delete all occurrences of "part" in filenames:
           python script.py -d part
        5. Delete part of the filename between "start" and "end":
           python script.py -dm start end
        6. Show help:
           python script.py -h
        """
    print(help_text)


def delete_min_mode(start,end,old_name):
    '''
    删除字符串start到字符串end之间的字符串，并将剩余的字符串替换为new_name。
    :param start:
    :param end:
    :param old_name:
    :return:
    '''
    if start == end:
        return delete_mode(start,old_name)
    old_name_prefixs = old_name.rsplit(".",1)
    start_index = old_name_prefixs[0].find(start)
    end_index = old_name_prefixs[0].find(end)
    if start_index == -1 or end_index == -1:
        print(f"Error: {start} or {end} not renamed")
        exit(1)
    if start_index > end_index:
        print(f"Error: {start} should be before {end}")
        print(f"Are you sure {start} and {end} switched?")
        a = input("y/n:")
        if a.lower()=='y':
            start_index, end_index = end_index,start_index
        else:
            exit(1)
    start_index = start_index + len(start)
    new_name_prefix = old_name_prefixs[0][:start_index] + old_name_prefixs[0][end_index:]
    return new_name_prefix+'.'+old_name_prefixs[-1]

def delete_mode(delete_part,old_name,n=None):
    '''
    当n为0或None时，删除所有字符串delete_part；，当n为正整数时，删除前n个delete_part；当n为负整数时，删除后n个delete_part。
    :param delete_part:
    :param old_name:
    :param n:
    :return:new_name
    '''
    old_name_parts = old_name.rsplit(".",1)
    if n is None or n==0:
        new_name_prefix = old_name_parts[0].replace(delete_part,"")
    elif n<0:#=replace本身不能使用负数，所以这里使用-n
        old_name_parts = old_name_parts[0][::-1]
        reverse_delete_part = delete_part[::-1]
        new_name_prefix = old_name_parts.replace(reverse_delete_part,"",-n)
        new_name_prefix = new_name_prefix[::-1]
    else:
        new_name_prefix = old_name_parts[0].replace(delete_part,"",n)
    new_name = new_name_prefix+'.'+old_name_parts[-1]

    return new_name



def prefix_mode(old_part,new_part,old_name):
    '''
    将字符串old_part替换为字符串new_part，并将字符串替换为new_name。
    :param old_part:
    :param new_part:
    :param old_name:
    :return:
    '''
    old_name_prefixs = old_name.rsplit(".",1)
    new_name_prefix = old_name_prefixs[0].replace(old_part,new_part)
    new_name = new_name_prefix+'.'+old_name_prefixs[-1]
    return new_name

def end_mode(new_part, old_name):
    try:
        old_name = old_name.rsplit('.',1)
        new_name = old_name[0]+'.'+new_part
        return new_name
    except:
        return old_name

def replace_name(old_name,new_name):
    if new_name == old_name:
        print(f"Error: {old_name} not renamed")
        exit(1)
    if os.path.isfile(old_name):
        try:
            shutil.move(old_name, new_name)
        except shutil.Error:
            print(f"Error: {new_name} already exists")
            print(f"Error: {old_name} not renamed")
            exit(1)

def my_rename(old_part, new_part,mode='-p'):
    old_names = os.listdir(os.getcwd())
    for old_name in old_names:
        if old_part not in old_name:
            continue
        if mode == '-a':
            new_name = old_name.replace(old_part, new_part)
            replace_name(old_name, new_name)
        elif mode == '-e':
            new_name = end_mode(new_part, old_name)
            replace_name(old_name, new_name)
        elif mode == "-p":#prefix mode
            new_name = prefix_mode(old_part, new_part, old_name)
            replace_name(old_name, new_name)
        elif mode == "-d":
            new_name = delete_mode(old_part, old_name)
            replace_name(old_name, new_name)
        elif mode == "-dm":
            new_name = delete_min_mode(old_part, new_part, old_name)
            replace_name(old_name, new_name)

def main():
    print(f"Received arguments: {sys.argv}")
    if sys.argv[1]=="-h":
        help_mode()
        exit(0)
    if len(sys.argv)==3 and sys.argv[1]!="-d":
        old_name = sys.argv[1]
        new_name = sys.argv[2]
        my_rename(old_name, new_name)
    elif len(sys.argv)==3 and sys.argv[1]=="-d":
        delete_part = sys.argv[2]
        my_rename(delete_part, None, mode="-d")
    elif len(sys.argv)==4:
        old_name = sys.argv[2]
        new_name = sys.argv[3]
        mode = sys.argv[1]
        if mode in ['-a', '-e', '-p','-dm','-h']:
            my_rename(old_name, new_name, mode)
        else:
            print("Error: Invalid mode")
            exit(1)
if __name__ == "__main__":
    main()