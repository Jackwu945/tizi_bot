import asyncio
import random
import re

import pymysql
import datetime
import time
import calculate
import res
import get_leader
import mcl.play
from threading import Thread

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import *
from graia.scheduler import GraiaScheduler, timers
from graia.ariadne.message.element import Plain, At, Image, Quote
from graia.ariadne.model import MiraiSession, Member, Group

# v1.0.0及以上
from pymysql.converters import escape_string

# 常量
cuoyicuo_say = ['再戳就要...就要被玩坏啦!', 'ばが、変態！', '烦诶', '仲咩？',"再戳把你绑起来!","不要再戳了...直接来吧！","别乱摸了啦","你戳到了奇怪的地方了!","啊!...不要戳这里","呜!","啊!","不要戳,我怕痒...呜呜呜","再戳咬断你手指(超凶)","(躲)","反击~","你欺负我...我这就去告诉主人!...呜呜"]
max_show = 5
cd = 20
max_say_hold = 5
manager_list = [1440239038, 179528936, 721265310]
chatrank_group = [1136462265, 699726067, 704397430, 782748255, 634522040, 282012452,297643538]
chatrank_group_tmp = [782748255, 884706171]
hello_send_group = [699726067, 1136462265,297643538]
leader_uid = {2709173: [634522040], 293793435: [1136462265],
              235098388: [884706171, 634522040, 1136462265], 188832903: [1136462265]}  # b站uid与群号相对应
name = {2709173: "高木头子", 293793435: "易姐酱", 235098388: "主人桑", 188832903: "🐟"}
new = {}
caller_and_qid = {}
for l in leader_uid:
    new[l] = (get_leader.getnow(l))

# 变量
callbacklist = []
said_list = []
timenudge = time.time()
time_get_tkg = time.time() - 10
# 初始化
loop = asyncio.new_event_loop()
bcc = Broadcast(loop=loop)
# 定义app
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="",  # 填入 HTTP API 服务运行的地址
        verify_key="",
        account=,  # 你的机器人的 qq 号
    )
)

# 测试图片
with open('test.jpg', 'rb') as f:
    pic = f.read()

with open('takagi.jpg', 'rb') as f:
    tkgwelcome = f.read()

# 定时任务初始化
sche = GraiaScheduler(loop=loop, broadcast=bcc)

def tech_test():
    time1=time.time()
    top = 10  # 显示几个?
    # say_count_qq={}
    exception = "会让bot出现Exception的屑用户"

    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    for g in chatrank_group:
        sql = "select * from tizibot where qgroup='{}'".format(g)
        cursor.execute(sql)
        result = cursor.fetchall()
        dt = datetime.now().strftime("%Y-%m-%d")  # 获取现在年月日
        say_count_name_times = {}
        for row in result:
            if str(dt) in str(row[0]):  # 是今天且是本次遍历的群
                if ' ' in row[2]:  # 名字是空格记录可能会有bug???
                    name = exception
                else:
                    name = row[2]
                # if row[1] not in say_count_qq:
                if row[2] not in say_count_name_times:
                    # say_count_qq[row[1]] = 1
                    say_count_name_times[name] = 1
                else:
                    # say_count_qq[row[1]] += 1
                    say_count_name_times[name] += 1

        say_count_name = sorted(say_count_name_times.items(), reverse=True,
                                key=lambda kv: (kv[1], kv[0]))  # 排序,返回列表,内容为人名和发言次数元组

        # 填充格式
        formattedmsg = "技术测试,三秒后撤回(群号{})\n".format(top, g)

        i = 0
        for s in say_count_name:
            if i == top:
                break

            formattedmsg += "第{}名:{}  发言次数:{}\n".format(i + 1, s[0], s[1])
            i += 1
        time2=time.time()
        formattedmsg+="用时{}".format(time2-time1)
        return formattedmsg

def get_qstn(vip):
    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    sql = "select * from TKG_qstn"
    cursor.execute(sql)
    result = cursor.fetchall()
    if vip == False:
        qid = random.randint(0, len(result))
    else:
        qid = 49
    return result[qid], qid


def verify(answer, qid):
    compare = {' A': 1, ' B': 2, ' C': 3, ' D': 4}
    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    sql = "select * from TKG_qstn"
    cursor.execute(sql)
    result = cursor.fetchall()

    righr_ans = result[qid][5]
    print(compare[answer[0]], righr_ans)
    if compare[answer[0]] == int(righr_ans):
        return True, 0
    else:
        return False, result[int(qid)][int(righr_ans)]


def piehung(group, ids, e):  # 算pie的线程
    app.sendMessage(group, MessageChain.create(
        [At(ids), Plain(mcl.play.main(e))]))


def tkg_daycall():
    tkgindex = random.randint(0, 178)
    try:  # 尝试打开该序号的图片,假定为jpg
        with open('takagisan/tkg{}.jpg'.format(tkgindex), 'rb') as f:
            tkgtoday = f.read()
    except:  # 打开失败,则以png打开
        with open('takagisan/tkg{}.png'.format(tkgindex), 'rb') as f:
            tkgtoday = f.read()
    return tkgtoday


# 定时任务函数开始
@sche.schedule(timers.crontabify("59 23 * * * 00"))
async def per_day(app: Ariadne):
    top = 10  # 显示几个?
    # say_count_qq={}
    exception = "会让bot出现Exception的屑用户"

    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    for g in chatrank_group:
        sql = "select * from tizibot where qgroup='{}'".format(g)
        cursor.execute(sql)
        result = cursor.fetchall()
        dt = datetime.now().strftime("%Y-%m-%d")  # 获取现在年月日
        say_count_name_times = {}
        for row in result:
            if str(dt) in str(row[0]):  # 是今天且是本次遍历的群
                if ' ' in row[2]:  # 名字是空格记录可能会有bug???
                    name = exception
                else:
                    name = row[2]
                # if row[1] not in say_count_qq:
                if row[2] not in say_count_name_times:
                    # say_count_qq[row[1]] = 1
                    say_count_name_times[name] = 1
                else:
                    # say_count_qq[row[1]] += 1
                    say_count_name_times[name] += 1

        say_count_name = sorted(say_count_name_times.items(), reverse=True,
                                key=lambda kv: (kv[1], kv[0]))  # 排序,返回列表,内容为人名和发言次数元组

        # 填充格式
        formattedmsg = "欸嘿嘿,又到了每天的最后一分钟啦,下面公布群发言榜Top{}(群号{})\n".format(top, g)

        i = 0
        for s in say_count_name:
            if i == top:
                break

            formattedmsg += "第{}名:{}  发言次数:{}\n".format(i + 1, s[0], s[1])
            i += 1

        await app.sendGroupMessage(g, MessageChain.create(formattedmsg))


# 每日高木
@sche.schedule(timers.crontabify("30 06 * * * 00"))
async def tkg_morning():
    daymsg = "各位哦哈哟,好好珍惜今天的早晨时光吧~\n"
    tkgtoday = tkg_daycall()
    for g in hello_send_group:
        await app.sendGroupMessage(g, MessageChain.create(Plain(f"{daymsg}\n这是本时段高木,请查收!\n"),
                                                          Image(data_bytes=tkgtoday)))


@sche.schedule(timers.crontabify("00 12 * * * 00"))
async def tkg_noon():
    daymsg = "各位中午好,别忘了去淦中午饭哦~\n"
    tkgtoday = tkg_daycall()
    for g in hello_send_group:
        await app.sendGroupMessage(g, MessageChain.create(Plain(f"{daymsg}\n这是本时段高木,请查收!\n"),
                                                          Image(data_bytes=tkgtoday)))


@sche.schedule(timers.crontabify("00 18 * * * 00"))
async def tkg_evening():
    daymsg = "各位晚上好,快去储备点晚上做夜猫子的能量吧~?\n"
    tkgtoday = tkg_daycall()
    for g in hello_send_group:
        await app.sendGroupMessage(g, MessageChain.create(Plain(f"{daymsg}\n这是本时段高木,请查收!\n抽高木功能回归啦！请私聊我发送 “抽高木” 吧！"),
                                                          Image(data_bytes=tkgtoday)))


@sche.schedule(timers.crontabify("00 00 * * * 00"))
async def tkg_evening():
    daymsg = "新的一天到来了,各位早点休息哦~\n"
    tkgtoday = tkg_daycall()
    for g in hello_send_group:
        await app.sendGroupMessage(g, MessageChain.create(Plain(f"{daymsg}\n这是本时段高木,请查收!\n抽高木功能回归啦！请私聊我发送 “抽高木” 吧！"),
                                                          Image(data_bytes=tkgtoday)))


@sche.schedule(timers.crontabify("*/1 * * * *"))
async def tkg_leader_get():
    global new, leader_uid
    for l in leader_uid:
        print(get_leader.getnow)
        if get_leader.getnow(l) != new[l]:
            r = get_leader.getcontext(l)
            for qgroup in leader_uid[l]:
                await app.sendGroupMessage(qgroup, MessageChain.create(
                    "{}发布了{},快去围观吧!\n内容:{}\n链接:https://t.bilibili.com/{}".format(name[l], r[0], r[1],
                                                                                 get_leader.getnow(l))))
                new[l] = (get_leader.getnow(l))


# @sche.schedule(timers.crontabify("* */1 * * * *"))
# async def hrs():
#     await app.sendGroupMessage(634522040, MessageChain.create("每半小时宣传\n我的主人接起了高木头子直播大旗，今晚12：25准时开播！\n 各位可以使用手机浏览器或电脑kmplayer等m3u播放器打开，网址：http://119.91.153.27/srs/trunk/objs/nginx/html/live/livestream/livestream.m3u8"))


# 供单次调用
def per_call(qgroup):
    time1=time.time()
    top = 10  # 显示几个?
    # say_count_qq={}
    exception = "会让bot出现Exception的屑用户"

    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    sql = "select * from tizibot where qgroup='{}'".format(qgroup)
    cursor.execute(sql)
    result = cursor.fetchall()
    say_count_name_times = {}
    for row in result:
        if ' ' in row[2]:  # 名字是空格记录可能会有bug???
            name = exception
        else:
            name = row[2]
        # if row[1] not in say_count_qq:
        if row[2] not in say_count_name_times:
            # say_count_qq[row[1]] = 1
            say_count_name_times[name] = 1
        else:
            # say_count_qq[row[1]] += 1
            say_count_name_times[name] += 1

    say_count_name = sorted(say_count_name_times.items(), reverse=True,
                            key=lambda kv: (kv[1], kv[0]))  # 排序,返回列表,内容为人名和发言次数元组

    # 填充格式
    formattedmsg = "群发言榜总榜Top{}(群号{})\n".format(top, qgroup)

    i = 0
    for s in say_count_name:
        if i == top:
            break
        formattedmsg += "第{}名:{}  发言次数:{}\n".format(i + 1, s[0], s[1])
        i += 1
    time2=time.time()
    formattedmsg+="用时{}秒".format(time2-time1)

    return formattedmsg


def tkg_percall():
    tkgindex = random.randint(0, 178)
    tkgget = random.randint(0, 1)
    if tkgget == 1 or tkgget == 0:
        try:  # 尝试打开该序号的图片,假定为jpg
            with open('takagisan/tkg{}.jpg'.format(tkgindex), 'rb') as f:
                tkgtoday = f.read()
        except:  # 打开失败,则以png打开
            with open('takagisan/tkg{}.png'.format(tkgindex), 'rb') as f:
                tkgtoday = f.read()
        return tkgtoday
    else:
        return "faild"

# 消息监听,关键词回复
@bcc.receiver("FriendMessage")
async def f_message_listener(app: Ariadne,message: MessageChain):
    msg = message.asPersistentString()
    if '技术测试' in msg:
        r=tech_test()
        await app.sendFriendMessage(179528936, MessageChain.create(r))

# 消息监听,关键词回复
@bcc.receiver("TempMessage")
async def s_message_listener(app: Ariadne, member: Member, message: MessageChain):
    msg = message.asPersistentString()
    global callbacklist, manager_list, time_get_tkg, caller_and_qid
    if '抽高木' in msg:  # 帮助
        now = time.time()
        if now - time_get_tkg > 0:  # 暂时不用
            img = tkg_percall()
            if img != "faild":
                await app.sendTempMessage(member.id, MessageChain.create(Plain("哇,居然是!\n"), Image(data_bytes=img)),
                                          634522040)
                time_get_tkg = now
            else:
                await app.sendTempMessage(member.id, MessageChain.create(
                    Plain("真可惜,没抽中")), 634522040)
        else:
            await app.sendTempMessage(member.id,
                                      MessageChain.create(Plain("本技能在冻结中（\n还剩{}秒".format(int(now - time_get_tkg)))),
                                      634522040)
    elif '题库抽取' in msg:
        r, qid = get_qstn(vip=False)

        caller_and_qid[member.id] = qid

        await app.sendTempMessage(member.id, MessageChain.create(At(member.id), Plain(
            " 高木问答题库抽取(仅限触发者{}以回复方式回答)\n问题:{}\nA:{}\nB:{}\nC:{}\nD:{}".format(member.name, r[0], r[1], r[2], r[3],
                                                                              r[4]))), 634522040)
    if message.has(Quote):
        if message.has(At):
            at = message.get(At)
            Q = message.get(Quote)
            if at[0].target == 2018957703:
                print(True)
                ans = re.findall(" +[A-D]", msg)
                if ans:
                    tf, answer = verify(ans, caller_and_qid[member.id])
                    if tf:
                        await app.sendMessage(member.group, MessageChain.create([At(member.id), Plain('恭喜你回答正确')]))
                    else:
                        await app.sendMessage(member.group,
                                              MessageChain.create([At(member.id), Plain('回答错误，答案是{}'.format(answer))]))



# 消息监听,关键词回复
@bcc.receiver("GroupMessage")
async def g_message_listener(app: Ariadne, member: Member, message: MessageChain, source: Source):
    global callbacklist, manager_list, time_get_tkg, callbackid

    if len(said_list) == 5:  # 群员发言列表等于5,清最旧
        said_list.pop(0)

    # 数据库记录模块
    db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot", charset='utf8')
    cursor = db.cursor()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = str(message.asSendable())

    sql = "INSERT INTO `tizibot` (`datetime`,`QQ`,`Qname`, `Qgroup`, `msg`) VALUES ('{}','{}','{}', '{}', '{}');".format(
        dt, member.id, escape_string(member.name), member.group.id, escape_string(msg))
    try:
        cursor.execute(sql)  # 执行sql
        db.commit()  # 提交
    except Exception as e:
        await app.sendFriendMessage(179528936,
                                    MessageChain.create(Plain("sql上传出错\n" + str(e) + "涉事SQL:{}".format(sql))))
    # (对性能影响待考究)
    cursor.close()  # 关指针
    db.close()  # 关库

    # 关键词判断块
    msg = message.asPersistentString()
    if msg == '梯子在吗':  # 普通关键词demo
        await app.sendMessage(member.group, MessageChain.create("我在"))
    if re.findall("[?？]", msg) != []:
        if '图片测试' in msg:  # 发送图片demo
            await app.sendMessage(member.group, MessageChain.create(Plain('test-->'), Image(data_bytes=pic)))
        elif '资源' in msg:  # 获取系统资源
            await app.sendMessage(member.group, MessageChain.create(res.get()))
        elif 'help' in msg:  # 帮助
            await app.sendMessage(member.group,
                                  MessageChain.create("http://jackwu.shakaianee.top/?p=244\n本文还在编写中，仅供预览！"))
        elif '抽高木' in msg:  # 帮助
            now = time.time()
            if now - time_get_tkg > 0:  # 暂时不用
                img = tkg_percall()
                if img != "faild":
                    await app.sendFriendMessage(member.id,
                                                MessageChain.create(Plain("哇,居然是!\n"), Image(data_bytes=img)))
                    time_get_tkg = now
                else:
                    await app.sendFriendMessage(member.id, MessageChain.create(
                        Plain("真可惜,没抽中")))
            else:
                await app.sendFriendMessage(member.id, MessageChain.create(
                    Plain("本技能在冻结中（\n还剩{}秒".format(int(now - time_get_tkg)))))
        elif '总排行' in msg:  # 帮助
            try:
                msg = per_call(member.group.id)
                await app.sendMessage(member.group, MessageChain.create(msg))
            except:
                msg = per_call(member.group.id)
                await app.sendMessage(member.group, MessageChain.create(msg))
        elif '最近撤回' in msg:  # 最近撤回展示功能
            formattedmsg = "最近撤回(设定仅显示{}条)\n".format(max_show)
            for call in callbacklist:
                formattedmsg += "撤回者:{} | 撤回内容:{}\n".format(call['callbacker'], call['msg'])
            callbackid = await app.sendMessage(member.group, MessageChain.create(Plain(formattedmsg)))
        elif '计算 ' in msg:  # 计算器
            cal = msg.replace("?计算 ", "")
            r = calculate.calc(cal)
            await app.sendMessage(member.group, MessageChain.create([Plain(r)]))
        elif '算pie ' in msg:  # 调用play.py
            e = int(msg.replace("?算pie ", ""))
            if e > 18000000:
                if e > 999999999999:
                    await app.sendMessage(member.group, MessageChain.create([Plain("精度太大了,这边建议你使用超算呢")]))
                    return
                await app.sendMessage(member.group,
                                      MessageChain.create([Plain("计算数位大,预计需要{}秒.届时我会@你".format(int(e / 18000000)))]))
                Thread(target=piehung, args=[member.group, member.id, e]).start()
        elif '题库抽取' in msg:
            if True:
                r, qid = get_qstn(vip=False)

                caller_and_qid[member.id] = qid

                await app.sendMessage(member.group, MessageChain.create(At(member.id), Plain(
                    " 高木问答题库抽取(仅限触发者{}以回复方式回答)\n问题:{}\nA:{}\nB:{}\nC:{}\nD:{}".format(member.name, r[0], r[1], r[2],
                                                                                      r[3],
                                                                                      r[4]))))
        elif '特定题目抽取' in msg:
            r, qid = get_qstn(vip=True)

            caller_and_qid[member.id] = qid

            await app.sendMessage(member.group, MessageChain.create(At(member.id), Plain(
                " 测试功能，但没加鉴权，不要乱触发\n问题:{}\nA:{}\nB:{}\nC:{}\nD:{}".format(r[0], r[1], r[2], r[3],
                                                                          r[4]))))
        elif "关键词添加" in msg:
            try:
                msg.replace("关键词添加","")
                add=msg.split(" ")
                db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot",
                                     charset='utf8')
                cursor = db.cursor()
                sql = "INSERT INTO `QA`(`Q`, `A`) VALUES ('{}','{}')".format(add[1],add[2])
                cursor.execute(sql)
                db.commit()
                await app.sendMessage(member.group, MessageChain.create([At(member.id), Plain('提交成功!')]))
            except Exception as e:
                await app.sendMessage(member.group, MessageChain.create([At(member.id), Plain('提交失败,'
                                                                                              '请检查下是不是用法错误?已反馈给主人\nexception:{}'.format(e))]))

            db.close()
            cursor.close()

    if message.has(Quote):
        if message.has(At):  # 关闭
            at = message.get(At)
            Q = message.get(Quote)
            if at[0].target == 2018957703:
                print(True)
                ans = re.findall(" +[A-D]", msg)
                if ans:
                    tf, answer = verify(ans, caller_and_qid[member.id])
                    if tf:
                        await app.sendMessage(member.group, MessageChain.create([At(member.id), Plain('恭喜你回答正确')]))
                    else:
                        await app.sendMessage(member.group,
                                              MessageChain.create([At(member.id), Plain('回答错误，答案是{}'.format(answer))]))

    if message.has(At):  # 出现At
        at = message.get(At)
        if at[0].target == 2018957703:
            if "嘘" in msg:
                await app.recallMessage(callbackid)
            elif '爬' in msg and member.id in manager_list:
                await app.sendMessage(member.group, MessageChain.create([Plain('我这就爬，呜呜呜~~~（loop stopped）')]))
                loop.stop()
            elif not message.has(Quote):
                statement=False
                db = pymysql.connect(host="localhost", user="tizibot", password="12321", database="tizibot",
                                     charset='utf8')
                cursor = db.cursor()
                sql = "select * from QA"
                cursor.execute(sql)
                result = cursor.fetchall()

                for r in result:
                    if r[0] in msg:
                        await app.sendMessage(member.group, MessageChain.create([Plain(r[1])]),quote=message.getFirst(Source))
                        statement=True
                        break
                if not statement :
                    await app.sendMessage(member.group,
                                          MessageChain.create([Plain("还没这个关键词回复哦~\n尝试   ?关键词添加 [问题] [答案]   来添加吧!")]),
                                          quote=message.getFirst(Source))

                db.close()
                cursor.close()

        # 若继续添加关键词,需继续写elif


# 事件触发模块
@bcc.receiver(MemberJoinEvent)  # 群员入群事件
async def join_event(app: Ariadne, group: Group, event: MemberJoinEvent):
    await app.sendMessage(event.member.group, MessageChain.create(
        [Plain('隆重介绍:我是本群最废废物JackWu的爱姬--梯子Bot\nJackWu群地位再次-1'), Image(data_bytes=tkgwelcome)]))


@bcc.receiver(MemberLeaveEventQuit)  # 群员退群事件
async def leave_event(app: Ariadne, event: MemberLeaveEventQuit):
    await app.sendMessage(event.member.group, MessageChain.create([Plain('{}被吓跑了呢~'.format(event.member.name))]))


@bcc.receiver(MemberLeaveEventKick)  # 群员被踢事件
async def leave_event(app: Ariadne, event: MemberLeaveEventKick):
    await app.sendMessage(event.member.group,
                          MessageChain.create([Plain('{}被管理员赠送了飞机票一张呢!~'.format(event.member.name))]))


@bcc.receiver(MemberHonorChangeEvent)  # 龙王(待测试)
async def member_honor_change_event(app: Ariadne, group: Group, event: MemberHonorChangeEvent):
    if event.action == "Active" and event.honor == "TALKATIVE":
        await app.sendMessage(
            group, MessageChain.create([
                Plain(text=f"恭喜 {event.member.name} 成为今天的龙王，喷个水呗?")
            ])
        )


@bcc.receiver(NudgeEvent)  # 戳一戳事件
async def member_nudge(app: Ariadne, event: NudgeEvent):
    global timenudge
    if event.target == 2018957703:  # 被戳者是不是我可爱的梯子bot?
        now = time.time()
        print(now - timenudge > cd)
        if now - timenudge > cd:
            if random.randint(0,1) == 1:
                await app.sendGroupMessage(event.group_id, MessageChain.create([Plain(random.choice(cuoyicuo_say)+"(戳回去)")]))
                await app.sendNudge(event.supplicant,event.group_id)
            else:
                await app.sendGroupMessage(event.group_id, MessageChain.create([Plain(random.choice(cuoyicuo_say))]))
            timenudge = time.time()

# 5秒后撤回示例
# await asyncio.sleep(5)
# await app.recallMessage(recall)


@bcc.receiver(GroupRecallEvent)  # 撤回事件  if块中撤回展示的数据产生源
async def member_recall(event: GroupRecallEvent):
    global callbacklist

    if len(callbacklist) == max_show:  # 撤回展示列表等于最大展示量,清最旧
        callbacklist.pop(0)  # 0元素为最旧撤回消息

    # 撤回的消息id,通过查询获得内容
    msg = await app.getMessageFromId(event.messageId)
    try:
        imgurl = msg.messageChain.getFirst(Image).url
        callbacklist.append({"callbacker": event.operator.name, 'msg': MessageChain.create(
            msg.messageChain.asSendable(), Plain("图片url：{}".format(imgurl)))})
    except:
        callbacklist.append({"callbacker": event.operator.name, 'msg': msg.messageChain.asSendable()})  # 压缩写法,请注意


loop.run_until_complete(app.lifecycle())
