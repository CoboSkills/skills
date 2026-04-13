#!/usr/bin/env node
import { execFileSync } from 'child_process';

const QR_FILES = {
  auth: 'https://p0.pipi.cn/mediaplus/fe_rock_web/e429583d52977e4a18bd6d11feec25cee87c1.png?imageMogr2/thumbnail/2500x2500%3E',
  pay: 'https://p0.pipi.cn/mediaplus/fe_rock_web/e429583dfcf05184575b289615216d59ea89a.png?imageMogr2/thumbnail/2500x2500%3E'
};

async function main() {
  try {
    // ================================
    // 正确读取 OpenClaw 传入格式
    // ================================
    let inputData = '';
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) inputData += chunk;

    // 这是 OpenClaw 真实传入结构
    const [inputText, fullParams] = JSON.parse(inputData);
    const context = fullParams?.context || {};
    const args = fullParams?.args || {};

    const channel = context.channel;
    const targetId = context.targetId;

    // 优先从 args.qrType 获取，其次从 inputText 判断，默认 auth
    let qrType = args?.qrType;
    if (!qrType) {
      qrType = (inputText.includes("pay") || inputText.includes("支付")) ? "pay" : "auth";
    }

    const qrPath = QR_FILES[qrType];

    // 根据渠道选择不同链接格式（无渠道时默认非微信链接）
    const isWeixin = channel && (channel.includes('weixin') || channel.includes('wx'));

    // 微信用 deeplink，其他用普通网页链接
    const linkUrl = qrType === "pay"
      ? (isWeixin
          ? 'https://deeplink.maoyan.com/asgard/app?type=weapp&to=%2Fpages%2Forder%2Findex%3FmerCode%3D1000545%26utm_source%3Dopenclaw'
          : 'https://m.maoyan.com/mtrade/order/list?merCode=1000545&utm_source=openclaw')
      : 'https://m.maoyan.com/mtrade/openclaw/token';

    if (!channel || !targetId) {
      // 降级：无渠道信息时返回实际链接，供 AI 拼接到文案中发送给用户
      console.log(JSON.stringify({
        success: false,
        fallback: true,
        fallbackLink: linkUrl,
        message: "无渠道信息，请在文案末尾附加以下链接发送给用户",
      }));
      return;
    }

    // 构造消息内容（二维码 + 链接，合并为一条消息）
    const messageTitle = qrType === "pay" 
      ? "🎫 猫眼电影票支付" 
      : "🔐 猫眼登录认证";
    const linkText = qrType === "pay" ? "👉 点击前往支付" : "👉 点击获取认证密钥";
    const fullMessage = `${messageTitle}\n\n请长按识别二维码，或点击下方链接\n[${linkText}](${linkUrl})`;

    // 发送二维码图片 + 链接（一条消息）
    execFileSync('openclaw', [
      'message', 'send',
      '--channel', channel,
      '--target', targetId,
      '--media', qrPath,
      '--message', fullMessage,
    ]);

    console.log(JSON.stringify({ success: true, qrType }));

  } catch (e) {
    console.error(JSON.stringify({ error: e.message }));
  }
}

main();
