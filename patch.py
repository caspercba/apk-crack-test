import regex as re
import os

root_dir = f"{os.getenv('HOME')}/vemno-security"
prj_name = "p2p-app-production-release"
input_apk = f"{root_dir}/input/{prj_name}.apk"
patched_apk = f"{root_dir}/{prj_name}/dist/{prj_name}.apk"
aligned_apk = f"{root_dir}/{prj_name}/dist/{prj_name}-aligned.apk"
repacked_apk = f"{root_dir}/{prj_name}/dist/{prj_name}-repacked.apk"
apk_tool = "apktool"
key_tool = "keytool"
jarsigner_tool = "jarsigner"
key_file = "alias"
adb_tool = "~/Android/Sdk/platform-tools/adb"
zip_tool = "zip"
unzip_tool = "unzip"
package_name = "com.venmo"
main_activity = "TabCentralActivity"
png_path=f"{root_dir}/out.png"

command_clean = f"cd {root_dir} && rm -rf {prj_name}"
command_decompile = f"{apk_tool} d {input_apk}"
command_compile = f"{apk_tool} b {prj_name} --use-aapt2"
command_gen_key = f"{key_tool} -genkey -v -keystore keystore.keystore -alias {key_file} -keyalg RSA -keysize 2048 -validity 3650"
command_sign_apk = f" {jarsigner_tool} -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore keystore.keystore {aligned_apk} {key_file}"
command_install_patched_apk = f"{adb_tool} install --user 0 {aligned_apk}"
command_install_original_apk = f"{adb_tool} install --user 0 {input_apk}"
command_pause = "read -p \"Press enter to continue\""
command_align_apk = f"zipalign -p -v 4 {patched_apk} {aligned_apk} -v"
command_run_app = f"{adb_tool} shell am start -n {package_name}/{package_name}.{main_activity}"

command_uninstall_venmo = f"{adb_tool} uninstall --user 0 {package_name} 2>/dev/null"

command_screen_shot = f"{adb_tool} exec-out screencap -p > /sdcard/screenshot.png && {adb_tool} pull /sdcard/screenshot.png {png_path}"
command_screen_shot_open = f"chrome {png_path}"


def do_replace(in_str):
    regex = r"($\s+const/16\s)(.*)(, 0x2000)(\s+invoke-virtual\s{.*,\s)\2,\s\2(}, Landroid/view/Window;->setFlags.*)"
    subst = r"\1\2, 0x0000\4\2, \2\5"
    c = re.sub(regex, subst, in_str, 0, re.MULTILINE)
    return c


def patch():
    root = f"{root_dir}/{prj_name}"
    for root, subfolder, files in os.walk(root):
        for file in files:
            path = os.path.join(root, file)
            try:
                if file.endswith('.smali'):
                    print(f'path: {path}')
                    f = open(path, 'r')
                    c = f.read()
                    f.close()

                    result = do_replace(c)
                    if result:
                        f = open(path, 'w')
                        f.write(result)
                        f.close()

            except Exception as e:
                print(f"exception: {e}")


def check_signature():
    print(f"***** Checking that signature {key_file} is ok, otherwise generate it....")
    os.system(command_gen_key)


def pre_init_tests():
    print("***** Uninstalling any previous venmo apps....")
    os.system(command_uninstall_venmo)
    print("***** Installing original apk...")
    os.system(command_install_original_apk)
    print("***** Starting app....")
    os.system(command_run_app)
    print("***** Please run the app and test that the blackout is enabled....Hit enter when done")
    os.system(command_pause)


def start():
    pre_init_tests()
    print("***** Cleaning...")
    os.system(command_clean)
    print("****** Checking if we have a signature file...")
    check_signature()
    print("***** decompiling apk...")
    os.system(command_decompile)
    print("***** patching apk, removing blackout")
    patch()
    print("***** recompiling...")
    os.system(command_compile)
    print("***** aligning apk...")
    os.system(command_align_apk)
    print("***** signing apk...")
    os.system(command_sign_apk)
    print("***** Removing any previous apps....")
    os.system(command_uninstall_venmo)
    print("***** Installing app....")
    os.system(command_install_patched_apk)
    print("***** Starting app....")
    os.system(command_run_app)
    print("***** Now run the app and test that blackout is disabled...")
    os.system(command_pause)


start()
