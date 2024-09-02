<script setup>
import {
    NButton, NInput, NIcon, NButtonGroup, NSpin,
    NInputGroup, NCard, NModal, NTabs, NTabPane, NInputNumber, NSelect,
    NTooltip,
    useMessage
} from 'naive-ui'
import { GameControllerOutline, GameController } from '@vicons/ionicons5'
import { LogInOutline as LogInIcon, SettingsOutline, Menu } from '@vicons/ionicons5'
import userAvatar from '@/assets/user-avatar.png';
import robotAvatar from '@/assets/robot-avatar.png';

import { Edit, Delete, Download } from '@vicons/carbon'
import Markdown from 'vue3-markdown-it';

import Login from './Login.vue'

import { reactive, ref, getCurrentInstance, watch, watchEffect, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router'
import html2canvas from "html2canvas";


const router = useRouter()
const route = useRoute()
const instaceV = getCurrentInstance()
const message = useMessage()

import { onMounted } from 'vue';

// 在组件的 setup 函数中添加
onMounted(() => {
  // 检查是否有会话记录
  if (left_data.chat.length > 0) {
    // 获取最后一个会话的 UUID
    const lastChatUuid = left_data.chat[left_data.chat.length - 1].uuid;
    // 路由跳转到最后一个会话
    router.push({ name: 'chat', params: { uuid: lastChatUuid } });
  } else {
    // 如果没有会话，设置左侧列表为空
    left_list_is_empty.value = true;
  }
});

// 控制侧边栏显示隐藏
var controlSidebarHidden = ref(true)
// 移动端下侧边栏显影

const showSetting = ref(false)

var LLM_APIKEY = ref("sk-cwtdeSy4Ownmy6Uh5e9b6a67Fe4c4454A3Dc524876348eB1")

var setting = reactive({
    server_url: 'http://localhost:8082/query', // 默认值
    type: 'query',
})

let left_list_is_empty = ref(false)

var is404 = ref(false)

var segmented = {
    content: 'soft',
    footer: 'soft'
}

var selectOptions = ref([
    {
        label: 'Query式访问',
        value: 'query'
    },
    {
        label: '流式访问',
        value: 'stream_log'
    }
])

var centerLodding = ref(false)

var input_area_value = ref('')
var left_data = reactive({
    left_list: [
        // { uuid: 1, title: 'New Chat1', enable_edit: false },
        // { uuid: 2, title: 'New Chat2', enable_edit: false },
    ],
    chat: [
        // {
        //     uuid: 1, msg_list: [
        //         { content: 'hello1', create_time: '2023-11-09 11:50:23', reversion: false, msgload: false },
        //     ]
        // },
        // {
        //     uuid: 2, msg_list: [
        //         { content: 'xxx', create_time: '2023-11-09 11:50:23', reversion: false, msgload: false },
        //     ]
        // },
    ],

})

// 监听响应式数据
watch(left_data, (newValue, oldValue) => {
    if (newValue.chat.length > 0) {
        left_list_is_empty.value = false
    } else {
        left_list_is_empty.value = true
    }
    localStorage.setItem('chatweb', JSON.stringify(newValue))
})

// 创建响应式变量后只执行一次输出的需求
watchEffect(() => {
    // 读取 localstorage
    const data = localStorage.getItem('chatweb')
    if (data) {

        const history = JSON.parse(data)
        left_data.left_list = history.left_list
        left_data.chat = history.chat
    } else {
        left_list_is_empty.value = true
    }
})



// 添加侧壁栏item
function addLeftListEle() {
    const uuid = randomUuid()
    left_data.left_list.push({
        uuid: uuid,
        title: `新的对话${uuid}`,
        enable_edit: false
    })
    left_data.chat.push({
        uuid: uuid,
        msg_list: []
    })

    // 路由跳转到最新的item
    router.push({ name: 'chat', params: { uuid: uuid } })

}
// 点击侧边栏某个item的编辑按钮
function editLeftListEle(uuid) {
    const index = left_data.left_list.findIndex(v => v.uuid == uuid)
    left_data.left_list[index].enable_edit = !left_data.left_list[index].enable_edit

    // all_data.left_list[index].enable_edit = !all_data.left_list[index].enable_edit
    // ls.updateLeftListItemEnableEditButton(uuid)

}

// 点击侧边栏某个item的删除按钮
async function delLeftListEle(uuid) {


    var index = left_data.left_list.findIndex(v => v.uuid == uuid)
    left_data.left_list.splice(index, 1)

    const chat_index = left_data.chat.findIndex(v => v.uuid == uuid)
    left_data.chat.splice(chat_index, 1)

    if (left_data.chat.length == 0) {
        left_list_is_empty = true
    } else {
        await nextTick()
        // 默认跳转到最新的 chat
        const last_chat_uuid = left_data.chat[left_data.chat.length - 1].uuid

        router.push({ name: 'chat', params: { "uuid": last_chat_uuid } })
    }
}

// 获取每个 chat 的msg list
function getMsgList(uuid) {

    if (uuid && uuid != undefined) {
        var index = left_data.chat.findIndex(v => v.uuid == uuid)
        if (index == -1) {
            return []
        }
        return left_data.chat[index].msg_list
    }
    return []

}

function randomUuid() {
    var len = 9
    var uuid = '';
    for (let i = 0; i < len; i++) {
        uuid += Math.floor(Math.random() * 10)
    }
    return Number(uuid, 10)
}

// 监听侧边栏item的回车事件
function submit(index) {
    editLeftListEle(index)
}

// 发送消息
function addMessageListItem(uuid) {
    if (input_area_value.value.length <= 2) {
        message.info('内容长度不得小于2')
        return false
    }
    var index = left_data.chat.findIndex(v => v.uuid == uuid)
    const now_t = (new Date()).toLocaleString('sv-SE', { "timeZone": "PRC" })
    left_data.chat[index].msg_list.push({
        content: input_area_value.value,
        create_time: now_t,
        reversion: true,
        msgload: false
    })

    const body = {
      config: {},
      input: input_area_value.value// 按要求的格式拼接

    };

    // 清空编辑框
    input_area_value.value = ''
    var ele = document.getElementById("msgArea")
    ele.scrollTop = ele.scrollHeight + ele.offsetHeight

    // 添加一个占位消息，表示正在加载
    left_data.chat[index].msg_list.push({
        content: '',
        create_time: now_t,
        reversion: false,
        msgload: true
    })
    console.info("开始发送消息...")


  // 使用编辑框中的 URL 进行请求
  const url = setting.server_url; // 获取 URL

  if (setting.type === 'stream_log') {
    startStream(index, body, url); // 传递 URL
  } else {
    startRequest(index, body, url); // 传递 URL
  }
}

function buildMessagePromt(index) {
    const res = []
    left_data.chat[index].msg_list.forEach(v => {
        let role = v.reversion ? 'user' : 'assistant'
        res.push({
            role: role,
            content: v.content
        })
    })
    res.pop()
    return res
}

async function startRequest(index, body, url) {
  const key = LLM_APIKEY.value;
  let response = null;

  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json", // 使用 JSON 作为接受格式
        "Authorization": `Bearer ${key}`, // 如果需要 API 密钥
      },
      mode: "cors",
      body: JSON.stringify(body),
    });

    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].msgload = false;
  } catch (error) {
    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += `发生了一些错误：${error.message}`;
    return false;
  }

  if (response.status !== 200) {
    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += `发生了一些错误：${response.status}-${response.statusText}`;
    return false;
  }

  try {
    const data = await response.json();
    if (data && data.output) { // 检查数据是否存在并包含 output
      const outputText = data.output;
      const currentContent = left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content;
      if (!currentContent.includes(outputText)) {
        left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += outputText;
      }
    } else {
      throw new Error('返回的数据结构不符合预期');
    }
  } catch (e) {
    console.error('Error parsing JSON:', e);
    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += '解析响应时发生错误';
  }

  return true; // 返回成功状态
}


async function startStream(index, body, url) {
  let response = null;

  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9"
      },
      mode: "cors",
      body: JSON.stringify(body),
    });

    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].msgload = false;
  } catch (error) {
    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += `发生了一些错误：${error.message}`;
    return false;
  }

  if (response.status !== 200) {
    left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += `发生了一些错误：${response.status}-${response.statusText}`;
    return false;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  const readStream = async () => {
    const { done, value } = await reader.read();

    if (done) {
      console.log('Stream reading complete');
      return;
    }

    buffer += decoder.decode(value, { stream: true });

    let completeData = '';
    let separatorIndex;
    while ((separatorIndex = buffer.indexOf('\n')) !== -1) {
      completeData = buffer.slice(0, separatorIndex).trim();
      buffer = buffer.slice(separatorIndex + 1);

      if (completeData.startsWith('data: ')) {
        const jsonString = completeData.slice(6); // 去掉 'data: '
        try {
          const data = JSON.parse(jsonString);
          data.ops.forEach(op => {
            if (op.op === 'add' && op.path.includes('/streamed_output')) {
              const outputText = op.value;
              if (outputText) {
                const currentContent = left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content;
                if (!currentContent.includes(outputText)) {
                  left_data.chat[index].msg_list[left_data.chat[index].msg_list.length - 1].content += outputText;
                }
              }
            }
          });
        } catch (e) {
          console.error('Error parsing JSON:', e, 'Complete Data:', completeData);
        }
      } else {
        console.log('No valid JSON found in:', completeData);
      }
    }

    return readStream();
  };

  return readStream();
}




function hasLogin(compomentName = 'Login') {
    if (compomentName == 'login') return instaceV.proxy.hasLogin ? 'hidden' : '';
    if (compomentName == 'main') return instaceV.proxy.hasLogin ? '' : 'hidden';
}

function showSettingFunc() {
    showSetting.value = !showSetting.value
}

// 删除当前会话记录
function deleteChatItemHistory(uuid) {
    const index = left_data.chat.findIndex(v => v.uuid == uuid);
    left_data.chat[index].msg_list = []
    message.success('当前会话记录已清理')
}

function confirmSettings() {
  // 这里可以添加保存设置的逻辑
  console.log("设置已确认:", setting);
  // 例如，你可以关闭模态框
  showSetting.value = false;
}

// 当前会话下载为图片
async function dom2img() {
    centerLodding.value = true

    var ele = document.querySelectorAll(".msgItem")
    var msgAreaDom = document.getElementById("msgArea")

    const width = msgAreaDom.offsetWidth * 2
    const height = msgAreaDom.scrollHeight * 1.5


    let canvas1 = document.createElement('canvas');
    let context = canvas1.getContext('2d');
    canvas1.width = width;
    canvas1.height = height;
    // 绘制矩形添加白色背景色
    context.rect(0, 0, width, height);
    context.fillStyle = "#fff";
    context.fill();

    let beforeHeight = 0
    for (let i = 0; i < ele.length; i++) {
        const dom_canvas = await html2canvas(ele[i], {
            scrollX: 0,
            scrollY: 0,
            height: ele[i].scrollHeight,
            width: ele[i].scrollWidth,
        })

        // var image = dom_canvas.toDataURL("image/png");
        context.drawImage(dom_canvas, 0, beforeHeight, dom_canvas.width, dom_canvas.height)
        beforeHeight = beforeHeight + dom_canvas.height;

    }
    var image = canvas1.toDataURL("image/png").replace("image/png", "image/octet-stream");
    var link = document.getElementById("link");
    link.setAttribute("download", `chatweb-${(new Date()).getTime()}.png`);
    link.setAttribute("href", image);
    link.click();

    centerLodding.value = false
    message.success('图片下载完成')

}




</script>

<template>
  <div>
    <div v-if="centerLodding" class="loading-container">
      <n-spin size="large" />
    </div>
    <Login class="border border-red-400" />
    <div class="flex flex-row h-min" :class="hasLogin('main')">
      <!-- 非移动端模式下侧边栏的样式 -->
      <div class="sidebar" :class="controlSidebarHidden ? 'w-0' : ''">
        <div class="hidden sm:flex sm:flex-col sm:h-screen sm:border">
          <!-- 新建按钮 -->
          <div class="basis-1/12 flex justify-center items-center">
            <n-button class="w-4/5" @click="addLeftListEle">新的会话</n-button>
          </div>
          <!-- 列表 -->
          <div class="basis-10/12 overflow-auto border">
            <div v-for="item in left_data.left_list" :key="item.uuid">
              <router-link :to="`/chat/${item.uuid}`" class="sidebar-item">
                <div class="w-4/5 flex items-center">
                  <n-icon size="medium">
                    <game-controller-outline />
                  </n-icon>
                  <div class="truncate mx-2" style="color: #000;">
                    <p v-if="!item.enable_edit" class="truncate h-full">{{ item.title }}</p>
                    <n-input v-else type="text" size="small" class="h-full" v-model:value="item.title" @keyup.enter="submit(item.uuid)" />
                  </div>
                </div>
                <div class="w-1/5 flex justify-center items-center" :class="route.params.uuid != item.uuid ? 'hidden' : ''">
                  <n-button-group size="small">
                    <n-button text @click="editLeftListEle(item.uuid)">
                      <n-icon><Edit /></n-icon>
                    </n-button>
                    <n-button text @click="delLeftListEle(item.uuid)">
                      <n-icon><Delete /></n-icon>
                    </n-button>
                  </n-button-group>
                </div>
              </router-link>
            </div>
          </div>
          <!-- 设置页面 -->
          <div class="footer flex flex-col items-center justify-between p-4 h-15">
            <div class="user-info font-bold text-lg">金融千问机器人</div>
            <div class="logo-container relative"> <!-- 添加一个容器 -->
              <img src="../assets/background.png" alt="Logo" class="logo" />
            </div>
            <div class="robot-description text-sm text-gray-600 mt-2">
              金融千问机器人，通过RAG对既有的PDF招股书建立了知识库，同时借助大模型+Agent对金融SQL数据库进行动态查询，旨在为用户提供快速、准确的金融信息和咨询服务。
            </div>
            <div class="settings-icon">
              <n-icon @click="showSettingFunc()">
                <SettingsOutline />
              </n-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 移动端模式下侧边栏的样式 -->
      <div class="sm:hidden absolute top-1 left-1 h-full w-full flex flex-col">
        <div>
          <n-button text style="font-size:32px" @click="controlSidebarHidden = !controlSidebarHidden">
            <n-icon class="text-black">
              <Menu />
            </n-icon>
          </n-button>
        </div>
        <div v-if="!controlSidebarHidden" class="mobile-sidebar">
          <div class="w-full flex flex-col h-screen border">
            <div class="basis-1/12 flex justify-center items-center">
              <n-button class="w-4/5" @click="addLeftListEle">新的对话</n-button>
            </div>
            <div class="basis-10/12 overflow-auto border">
              <div v-for="item in left_data.left_list" :key="item.uuid">
                <router-link :to="`/chat/${item.uuid}`" class="sidebar-item">
                  <div class="w-4/5 flex items-center">
                    <n-icon size="medium">
                      <game-controller-outline />
                    </n-icon>
                    <div class="truncate mx-2">
                      <p v-if="!item.enable_edit" class="truncate h-full">{{ item.title }}</p>
                      <n-input v-else type="text" size="small" class="h-full" v-model:value="item.title" @keyup.enter="submit(item.uuid)" />
                    </div>
                  </div>
                  <div class="w-1/5 flex justify-center items-center" :class="route.params.uuid != item.uuid ? 'hidden' : ''">
                    <n-button-group size="small">
                      <n-button text @click="editLeftListEle(item.uuid)">
                        <n-icon><Edit /></n-icon>
                      </n-button>
                      <n-button text @click="delLeftListEle(item.uuid)">
                        <n-icon><Delete /></n-icon>
                      </n-button>
                    </n-button-group>
                  </div>
                </router-link>
              </div>
            </div>
            <div class="footer flex items-center justify-between p-4 h-15">
              <div class="user-info font-bold">金融千问机器人</div>
              <div class="settings-icon">
                <n-icon @click="showSettingFunc()">
                  <SettingsOutline />
                </n-icon>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="w-full sm:w-4/5 h-full">
        <div class="flex flex-col h-screen">
          <div v-if="left_list_is_empty" class="empty-chat-message">
            Hi
          </div>
          <div v-else class="chat-area" id="msgArea">
            <div v-for="(msglist, index) in getMsgList(route.params.uuid)" :key="index" class="flex flex-col mt-1 msgItem">
              <div :class="msglist.reversion ? 'flex-row-reverse' : 'flex-row'" class="flex justify-start items-center h-10">

                <img
                    class="rounded-full avatar"
                    :src="msglist.reversion ? userAvatar : robotAvatar"
                    alt="头像"
                />
                <span class="ml-4 text-sm">{{ msglist.create_time }}</span>
              </div>
              <div class="flex" :class="msglist.reversion ? 'flex-row-reverse' : 'flex-row'">
                <div class="message-container">
                  <n-spin v-if="msglist.msgload" size="small" stroke="red" />
                  <Markdown v-else :source="msglist.content"></Markdown>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!left_list_is_empty" class="input-area">
            <div class="p-2">
              <n-input-group>
                <n-tooltip trigger="hover">
                  <template #trigger>
                    <n-button text size="large" class="px-2" @click="deleteChatItemHistory(route.params.uuid)">
                      <n-icon class="text-black">
                        <Delete />
                      </n-icon>
                    </n-button>
                  </template>
                  删除当前会话记录
                </n-tooltip>
                <n-tooltip trigger="hover">
                  <template #trigger>
                    <n-button text size="large" class="pr-4" @click="dom2img()">
                      <n-icon class="text-black">
                        <Download />
                      </n-icon>
                    </n-button>
                  </template>
                  下载当前会话为图片
                </n-tooltip>
                <a href="" id="link" class="hidden"></a>
                <n-input show-count @keyup.ctrl.enter="addMessageListItem(route.params.uuid)" placeholder="Ctrl+Enter 发送消息，发送消息长度需要大于2个字" v-model:value="input_area_value" type="textarea" size="tiny" :autosize="{ minRows: 2, maxRows: 5 }" />
                <n-button ghost class="h-auto" @click="addMessageListItem(route.params.uuid)">
                  发送
                </n-button>
              </n-input-group>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置模态框 -->
    <n-modal v-model:show="showSetting" style="width: 600px" class="custom-card" preset="card" title="设置">
      <n-tabs type="line" animated>
        <n-tab-pane name="about" tab="关于">
          <div>这是一个demo项目，仅用于学习。</div>
          <div class="my-4">技术栈：Vue3 + Vite + tailwindCss3 + NaiveUi</div>
        </n-tab-pane>
        <n-tab-pane name="settings" tab="设置">
          <div class="grid grid-rows-3 gap-4">
            <div>
              <span class="mr-4">Server URL: </span>
              <n-input v-model:value="setting.server_url" placeholder="请输入服务器 URL" />
            </div>
            <div>
              <span class="mr-4">type: </span>
              <n-select :style="{ width: '80%' }" :options="selectOptions" v-model:value="setting.type" />
            </div>
            <div class="flex justify-end">
              <n-button
                  @click="confirmSettings"
                  class="custom-button">
                确认
              </n-button>
            </div>
          </div>
        </n-tab-pane>
        <n-tab-pane name="other" tab="其他">
          其他
        </n-tab-pane>
      </n-tabs>
    </n-modal>
  </div>
</template>

<style scoped>
.router-link-active {
  border-color: #18a058;
  color: #18a058;
}

.loading-container {
  position: absolute;
  top: 33%;
  left: 33%;
  background-color: gray;
  width: 33%;
  height: 33%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.sidebar {
  width: 20%;
  height: 100%;
}

.sidebar-item {
  margin: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid gray;
  border-radius: 0.375rem; /* rounded-md */
  padding: 0.5rem;
  color: white;
}

.settings-container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  height: 50%;
}

.user-info {
  width: 50%;
  height: 100%;
  display: grid;
  grid-template-rows: repeat(2, 1fr);
}

.settings-icon {
  width: 25%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.mobile-sidebar {
  width: 80%;
  background-color: white;
  dark:bg-black;
}

.empty-chat-message {
  flex-basis: 91%;
  width: 100%;
  padding: 3rem;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  color: gray;
  font-style: italic;
}

.chat-area {
  flex-basis: 91%;
  width: 100%;
  padding: 3rem;
  overflow: auto;
}

.message-container {
  background-color: #bfdbfe; /* bg-blue-200 */
  color: black; /* dark:text-black */
  width: auto;
  max-width: 80%;
  min-width: 1%;
  break-words: break-word;
  overflow: hidden;
  border-radius: 0.375rem; /* rounded-sm */
  padding: 0.5rem;
  margin: 0.25rem 0;
}

.input-area {
  flex-basis: 8%;
  width: 100%;
}

.avatar {
  width: 50px;
  height: 50px;
}

.footer {
  text-align: center; /* 居中显示 */
}

.robot-description {
  margin-top: 8px; /* 描述与 Logo 之间的间距 */
  text-align: left; /* 左对齐 */
  width: 100%; /* 使描述占满可用宽度 */
  padding-left: 16px; /* 可选：增加左侧内边距 */
}

.logo-container {
  position: relative; /* 设置容器为相对定位 */
}

.background-logo {
  position: absolute; /* 设置背景图为绝对定位 */
  top: 0; /* 顶部对齐 */
  left: 0; /* 左侧对齐 */
  width: 240px; /* 设置背景图宽度为240px */
  height: auto; /* 保持比例 */
  z-index: 1; /* 确保背景图在logo下方 */
}

.logo {
  position: relative; /* 设置logo为相对定位 */
  z-index: 2; /* 确保logo在背景图上方 */
  width: 200px; /* 根据需要调整 Logo 大小 */
  height: auto; /* 保持比例 */
  top: 30%; /* 垂直居中 */
  left: 50%; /* 水平居中 */
  transform: translate(-50%, -50%); /* 使 logo 在背景图中心 */
}

.custom-button {
  background-color: #007bff; /* 按钮背景色 */
  color: white; /* 字体颜色 */
  border: none; /* 去掉边框 */
  padding: 10px 20px; /* 内边距 */
  border-radius: 5px; /* 圆角 */
  cursor: pointer; /* 鼠标样式 */
  transition: background-color 0.3s; /* 添加过渡效果 */
}

.custom-button:hover {
  background-color: #0056b3; /* 悬停时的背景颜色 */
}

</style>

