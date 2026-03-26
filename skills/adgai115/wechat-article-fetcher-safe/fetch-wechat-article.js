const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * 自动查找 Chrome 路径
 */
function findChromePath() {
  if (process.platform === 'win32') {
    const paths = [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe')
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) return p;
    }
  } else if (process.platform === 'darwin') {
    const p = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    if (fs.existsSync(p)) return p;
  } else {
    const paths = [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium'
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

/**
 * 抓取微信公众号文章
 * @param {Object} options - 配置选项
 * @param {string} options.url - 文章 URL
 * @param {boolean} options.saveToFile - 是否保存文件
 * @param {string} options.outputDir - 输出目录
 * @param {string} options.chromePath - Chrome 路径 (可选)
 * @returns {Promise<{title: string, author: string, time: string, content: string}>}
 */
async function fetchWechatArticle(options = {}) {
  const {
    url,
    saveToFile = true,
    outputDir = '.',
    chromePath = findChromePath()
  } = options;

  if (!url) {
    throw new Error('缺少文章 URL');
  }

  if (!chromePath) {
    throw new Error('未找到 Chrome 浏览器，请手动指定 chromePath 或安装 Chrome');
  }

  let browser;
  try {
    console.log('🚀 正在启动 Chrome...');
    
    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });
    
    console.log('✅ Chrome 已启动');
    
    const page = await browser.newPage();
    
    // 移动端 User-Agent
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0');
    await page.setViewport({ width: 375, height: 812 });
    
    console.log('📖 正在加载文章:', url);
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });
    
    console.log('✅ 页面加载完成');
    
    // 等待内容
    await page.waitForSelector('#js_content, .rich_media_content', { timeout: 10000 })
      .catch(() => console.log('⚠️  未找到标准内容选择器'));
    
    // 提取正文和元信息
    const articleData = await page.evaluate(() => {
      // 检查是否被拦截或页面已删除
      const titleEl = document.querySelector('#activity-name') || document.querySelector('title');
      const title = titleEl?.innerText?.trim() || '无标题';
      
      const isDeleted = document.body.innerText.includes('该内容已被发布者删除') || 
                        document.body.innerText.includes('此内容因违规无法查看');
      
      if (isDeleted) {
        return { error: '文章已被删除或违规下架' };
      }

      // 作者
      const author = document.querySelector('.rich_media_meta_nickname')?.innerText?.trim() || '未知';
      
      // 时间
      const time = document.querySelector('.rich_media_meta_text')?.innerText?.trim() || '未知';
      
      // 正文
      const selectors = ['#js_content', '.rich_media_content', '.rich_media_area_primary', 'article'];
      let content = '';
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText.trim().length > 10) {
          content = el.innerText.trim();
          break;
        }
      }
      
      if (!content) {
        // Fallback，移除明显的无关节点
        const clones = document.body.cloneNode(true);
        const removes = clones.querySelectorAll('script, style, nav, footer, .qr_code_pc, #js_profile_qrcode');
        removes.forEach(n => n.remove());
        content = clones.innerText.trim();
      }
      
      return { title, author, time, content };
    });

    if (articleData.error) {
      throw new Error(`页面异常: ${articleData.error}`);
    }
    
    console.log('\n📄 ========== 文章信息 ==========\n');
    console.log('标题:', articleData.title);
    console.log('作者:', articleData.author);
    console.log('时间:', articleData.time);
    console.log('\n📝 ========== 文章内容 ==========\n');
    console.log(articleData.content.substring(0, 500) + (articleData.content.length > 500 ? '...' : ''));
    console.log('\n========== 文章结束 ==========\n');
    
    // 保存文件
    if (saveToFile) {
      const filename = `article-wechat-${Date.now()}.txt`;
      const filepath = path.join(outputDir, filename);
      
      // 确保输出目录存在
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      fs.writeFileSync(filepath, 
        `标题：${articleData.title}\n作者：${articleData.author}\n时间：${articleData.time}\n\n${articleData.content}`, 
        'utf8'
      );
      console.log('💾 内容已保存到:', filepath);
    }
    
    await browser.close();
    console.log('🔒 浏览器已关闭');
    
    return articleData;
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    console.error(error.stack);
    if (browser) await browser.close();
    throw error;
  }
}

// 命令行支持
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--test')) {
    require('./tests/run-tests');
  } else {
    const url = args[0];
    
    if (!url || url.startsWith('-')) {
      console.log('用法：node fetch-wechat-article.js <文章 URL>');
      console.log('      node fetch-wechat-article.js --test  # 运行测试');
      console.log('示例：node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx');
      process.exit(1);
    }
    
    fetchWechatArticle({ url })
      .then(() => {
        console.log('✅ 抓取完成');
      })
      .catch((error) => {
        console.error('❌ 抓取失败:', error.message);
        process.exit(1);
      });
  }
}

module.exports = { fetchWechatArticle };
