
const KEY = 'ai_tool_tracker_v2';
const LEGACY = 'ai_tool_tracker';
const WEEK = ['周日','周一','周二','周三','周四','周五','周六'];
// 官方矢量商标（来源：simple-icons；OpenAI 取自原仓库）
const BRANDS = [
  { keys: ['openai', 'chatgpt', 'gpt'], color: '#ffffff', path: 'M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z' },
  { keys: ['anthropic', 'claude'], color: '#d97757', path: 'm4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z' },
  { keys: ['xai', 'grok'], color: '#ffffff', path: 'M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z' },
  { keys: ['cursor'], color: '#ffffff', path: 'M11.503.131 1.891 5.678a.84.84 0 0 0-.42.726v11.188c0 .3.162.575.42.724l9.609 5.55a1 1 0 0 0 .998 0l9.61-5.55a.84.84 0 0 0 .42-.724V6.404a.84.84 0 0 0-.42-.726L12.497.131a1.01 1.01 0 0 0-.996 0M2.657 6.338h18.55c.263 0 .43.287.297.515L12.23 22.918c-.062.107-.229.064-.229-.06V12.335a.59.59 0 0 0-.295-.51l-9.11-5.257c-.109-.063-.064-.23.061-.23' },
  { keys: ['kimi'], color: '#8b93ff', path: 'M13 1.5c4.69 0 8.5 3.81 8.5 8.5v4c0 4.69-3.81 8.5-8.5 8.5-1.66 0-3.22-.48-4.55-1.31l-7.16 3.41 3.42-7.06C3.58 16.18 3 14.4 3 12.5V10C3 5.31 6.81 1.5 13 1.5Zm-2 5.5v2h4v-2h-4Zm-3 4v2h10v-2H8Z' },
  { keys: ['moonshot', '月之暗面'], color: '#ff5c1f', path: 'M12 2 4 18h5l3-6.5L15 18h5L12 2Zm-7 18 2 4h4l-2-4H5Z' },
  { keys: ['agnes'], color: '#ff7a2e', path: 'M2 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0 2 4 0 8H2c-2-4-2-4 0-8Z' },
  { keys: ['perplexity'], color: '#20b8cd', path: 'M22.3977 7.0896h-2.3106V.0676l-7.5094 6.3542V.1577h-1.1554v6.1966L4.4904 0v7.0896H1.6023v10.3976h2.8882V24l6.932-6.3591v6.2005h1.1554v-6.0469l6.9318 6.1807v-6.4879h2.8882V7.0896zm-3.4657-4.531v4.531h-5.355l5.355-4.531zm-13.2862.0676 4.8691 4.4634H5.6458V2.6262zM2.7576 16.332V8.245h7.8476l-6.1149 6.1147v1.9723H2.7576zm2.8882 5.0404v-3.8852h.0001v-2.6488l5.7763-5.7764v7.0111l-5.7764 5.2993zm12.7086.0248-5.7766-5.1509V9.0618l5.7766 5.7766v6.5588zm2.8882-5.0652h-1.733v-1.9723L13.3948 8.245h7.8478v8.087z' },
  { keys: ['gemini', 'google'], color: '#4796e3', path: 'M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58 12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96 2.19.93 3.81 2.55t2.55 3.81' },
  { keys: ['deepseek'], color: '#4d6bfe', path: 'M23.748 4.651c-.254-.124-.364.113-.512.233-.051.04-.094.09-.137.137-.372.397-.806.657-1.373.626-.829-.046-1.537.214-2.163.848-.133-.782-.575-1.248-1.247-1.548-.352-.155-.708-.311-.955-.65-.172-.24-.219-.509-.305-.774-.055-.16-.11-.323-.293-.35-.2-.031-.278.136-.356.276-.313.572-.434 1.202-.422 1.84.027 1.436.633 2.58 1.838 3.393.137.094.172.187.129.323-.082.28-.18.553-.266.833-.055.179-.137.218-.328.14a5.5 5.5 0 0 1-1.737-1.179c-.857-.828-1.631-1.743-2.597-2.46a12 12 0 0 0-.689-.47c-.985-.957.13-1.743.387-1.836.27-.098.094-.433-.778-.428-.872.003-1.67.295-2.687.685a3 3 0 0 1-.465.136 9.6 9.6 0 0 0-2.883-.101c-1.885.21-3.39 1.1-4.497 2.622C.082 8.776-.231 10.854.152 13.02c.403 2.284 1.568 4.175 3.36 5.653 1.857 1.533 3.997 2.284 6.438 2.14 1.482-.085 3.132-.284 4.994-1.86.47.234.962.328 1.78.398.629.058 1.235-.031 1.705-.129.735-.155.684-.836.418-.961-2.155-1.004-1.682-.595-2.112-.926 1.095-1.295 2.768-3.598 3.284-6.733.05-.346.115-.834.108-1.114-.004-.171.035-.238.23-.257a4.2 4.2 0 0 0 1.545-.475c1.397-.763 1.96-2.016 2.093-3.517.02-.23-.004-.467-.247-.588M11.58 18.168c-2.088-1.642-3.101-2.183-3.52-2.16-.39.024-.32.472-.234.763.09.288.207.487.371.74.114.167.192.416-.113.603-.673.416-1.842-.14-1.897-.168-1.361-.801-2.5-1.86-3.301-3.306-.775-1.393-1.225-2.888-1.299-4.482-.02-.385.094-.522.477-.592a4.7 4.7 0 0 1 1.53-.038c2.131.311 3.946 1.264 5.467 2.774.868.86 1.525 1.887 2.202 2.89.72 1.066 1.494 2.082 2.48 2.915.348.291.626.513.892.677-.802.09-2.14.109-3.055-.615zm1.001-6.44a.306.306 0 0 1 .415-.287.3.3 0 0 1 .113.074.3.3 0 0 1 .086.214c0 .17-.136.307-.308.307a.303.303 0 0 1-.306-.307m3.11 1.596c-.2.081-.4.151-.591.16a1.25 1.25 0 0 1-.798-.254c-.274-.23-.47-.358-.551-.758a1.7 1.7 0 0 1 .015-.588c.07-.327-.007-.537-.238-.727-.188-.156-.426-.199-.689-.199a.6.6 0 0 1-.254-.078.253.253 0 0 1-.114-.358 1 1 0 0 1 .192-.21c.356-.202.767-.136 1.146.016.352.144.618.408 1.001.782.392.451.462.576.685.915.176.264.336.536.446.848.066.194-.02.353-.25.45' },
  { keys: ['copilot'], color: '#e9eaf0', path: 'M23.922 16.997C23.061 18.492 18.063 22.02 12 22.02 5.937 22.02.939 18.492.078 16.997A.641.641 0 0 1 0 16.741v-2.869a.883.883 0 0 1 .053-.22c.372-.935 1.347-2.292 2.605-2.656.167-.429.414-1.055.644-1.517a10.098 10.098 0 0 1-.052-1.086c0-1.331.282-2.499 1.132-3.368.397-.406.89-.717 1.474-.952C7.255 2.937 9.248 1.98 11.978 1.98c2.731 0 4.767.957 6.166 2.093.584.235 1.077.546 1.474.952.85.869 1.132 2.037 1.132 3.368 0 .368-.014.733-.052 1.086.23.462.477 1.088.644 1.517 1.258.364 2.233 1.721 2.605 2.656a.841.841 0 0 1 .053.22v2.869a.641.641 0 0 1-.078.256Zm-11.75-5.992h-.344a4.359 4.359 0 0 1-.355.508c-.77.947-1.918 1.492-3.508 1.492-1.725 0-2.989-.359-3.782-1.259a2.137 2.137 0 0 1-.085-.104L4 11.746v6.585c1.435.779 4.514 2.179 8 2.179 3.486 0 6.565-1.4 8-2.179v-6.585l-.098-.104s-.033.045-.085.104c-.793.9-2.057 1.259-3.782 1.259-1.59 0-2.738-.545-3.508-1.492a4.359 4.359 0 0 1-.355-.508Zm2.328 3.25c.549 0 1 .451 1 1v2c0 .549-.451 1-1 1-.549 0-1-.451-1-1v-2c0-.549.451-1 1-1Zm-5 0c.549 0 1 .451 1 1v2c0 .549-.451 1-1 1-.549 0-1-.451-1-1v-2c0-.549.451-1 1-1Zm3.313-6.185c.136 1.057.403 1.913.878 2.497.442.544 1.134.938 2.344.938 1.573 0 2.292-.337 2.657-.751.384-.435.558-1.15.558-2.361 0-1.14-.243-1.847-.705-2.319-.477-.488-1.319-.862-2.824-1.025-1.487-.161-2.192.138-2.533.529-.269.307-.437.808-.438 1.578v.021c0 .265.021.562.063.893Zm-1.626 0c.042-.331.063-.628.063-.894v-.02c-.001-.77-.169-1.271-.438-1.578-.341-.391-1.046-.69-2.533-.529-1.505.163-2.347.537-2.824 1.025-.462.472-.705 1.179-.705 2.319 0 1.211.175 1.926.558 2.361.365.414 1.084.751 2.657.751 1.21 0 1.902-.394 2.344-.938.475-.584.742-1.44.878-2.497Z' }
];

function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

const DEFAULTS = [
  { name: 'ChatGPT Plus', provider: 'OpenAI', category: 'chat', reset: { period: 'weekly', day: 2, hour: 0, minute: 0 }, expiry: { period: 'monthly', day: 11 }, quotaPct: 32 },
  { name: 'Claude Pro', provider: 'Anthropic', category: 'chat', reset: { period: 'weekly', day: 0, hour: 15, minute: 0 }, expiry: { period: 'monthly', day: 11 }, quotaPct: 26 },
  { name: 'Cursor', provider: 'Cursor', category: 'coding', reset: { period: 'monthly', day: 22, hour: 0, minute: 0 }, expiry: { period: 'monthly', day: 22 }, quotaPct: 36 },
  { name: 'Grok', provider: 'xAI', category: 'chat', reset: { period: 'weekly', day: 5, hour: 0, minute: 0 }, expiry: { period: 'monthly', day: 26 }, quotaPct: 51 },
  { name: 'Kimi', provider: 'Moonshot AI', category: 'chat', reset: { period: 'monthly', day: 18, hour: 0, minute: 0 }, expiry: { period: 'monthly', day: 18 }, quotaPct: 90 }
];

class Component extends DCLogic {
  // 模型选择网格（与 BRANDS 一一对应，最后一项为「自定义」）
  BRAND_GRID: [
    { id: 'openai',     label: 'ChatGPT',     provider: 'OpenAI',     color: '#10a37f', path: 'M22.282 9.821a5.985 5.985 0 0 0-.515-4.910 6.046 6.046 0 0 0-6.509-2.891 6.046 6.046 0 0 0-4.922 2.985m-.735 8.594a5.985 5.985 0 0 0 .515 4.910 6.046 6.046 0 0 0 6.509 2.891 6.046 6.046 0 0 0 4.922-2.985m-.735-8.594a5.985 5.985 0 0 1 .515-4.910 6.046 6.046 0 0 1 6.509-2.891 6.046 6.046 0 0 1 4.922 2.985M9.821 1.282a5.985 5.985 0 0 0-4.910.515 6.046 6.046 0 0 0-2.891 6.509 6.046 6.046 0 0 0 2.985 4.922' },
    { id: 'anthropic',  label: 'Claude',      provider: 'Anthropic',  color: '#d97757', path: 'M18.18 13.42a4.46 4.46 0 0 1-4.45 4.46h-4.3a4.46 4.46 0 0 1-4.46-4.46V10.1A4.46 4.46 0 0 1 9.43 5.64h4.3a4.46 4.46 0 0 1 4.45 4.46v3.32Z' },
    { id: 'cursor',     label: 'Cursor',      provider: 'Cursor',     color: '#ffffff', path: 'M4 2l7 20 2.5-8.5L22 11.5 4 2z' },
    { id: 'gemini',     label: 'Gemini',      provider: 'Google',     color: '#4285f4', path: 'M12 2l2.2 6.8L21 11l-6.8 2.2L12 20l-2.2-6.8L3 11l6.8-2.2L12 2z' },
    { id: 'perplexity', label: 'Perplexity',  provider: 'Perplexity', color: '#20808d', path: 'M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z' },
    { id: 'kimi',       label: 'Kimi',        provider: 'Moonshot AI', color: '#8b93ff', path: 'M13 1.5c4.69 0 8.5 3.81 8.5 8.5v4c0 4.69-3.81 8.5-8.5 8.5-1.66 0-3.22-.48-4.55-1.31l-7.16 3.41 3.42-7.06C3.58 16.18 3 14.4 3 12.5V10C3 5.31 6.81 1.5 13 1.5Zm-2 5.5v2h4v-2h-4Zm-3 4v2h10v-2H8Z' },
    { id: 'moonshot',   label: 'Moonshot AI', provider: 'Moonshot AI', color: '#ff5c1f', path: 'M12 2 4 18h5l3-6.5L15 18h5L12 2Zm-7 18 2 4h4l-2-4H5Z' },
    { id: 'deepseek',   label: 'DeepSeek',    provider: 'DeepSeek',   color: '#4d6bfe', path: 'M24 12a12 12 0 1 1-24 0 12 12 0 0 1 24 0Z' },
    { id: 'xai',        label: 'Grok',        provider: 'xAI',         color: '#9b9b9b', path: 'M13.87 2.64c.4 2.46 2.46 4.52 4.92 4.92v5.08h-5.08c-.4-2.46-2.46-4.52-4.92-4.92V7.56c2.46.4 4.52 2.46 4.92 4.92h5.08v-.04l-4.99-4.8Z' },
    { id: 'agnes',      label: 'Agnes',       provider: 'Agnes',      color: '#ff7a2e', path: 'M2 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0 2 4 0 8H2c-2-4-2-4 0-8Z' },
    { id: '__custom__', label: '自定义',      provider: '' }
  ],
  state = { tools: [], query: '', filter: 'all', modal: false, editId: null, form: this.blankForm(), brand: '', toasts: [], tick: 0 };

  blankForm() {
    return { name: '', provider: '', category: 'chat', resetPeriod: 'weekly', resetDay: '1', resetTime: '00:00', expiryPeriod: 'monthly', expiryDay: '7', quotaPct: '' };
  }

  // 由当前 name+provider 反向识别所属 brand（用于「编辑」时高亮已选项）
  detectBrand(form) {
    const hay = ((form.provider || '') + ' ' + (form.name || '')).toLowerCase();
    if (!hay.trim()) return '__custom__';
    const def = this.BRAND_GRID.find(b => b.id !== '__custom__' && b.provider && hay.includes(b.provider.toLowerCase()));
    if (def) return def.id;
    return '__custom__';
  }

  componentDidMount() {
    this.fileRef = React.createRef();
    let tools = [];
    try {
      const raw = localStorage.getItem(KEY) || localStorage.getItem(LEGACY);
      if (raw) tools = JSON.parse(raw) || [];
    } catch (e) { tools = []; }
    if (!Array.isArray(tools) || !tools.length) tools = DEFAULTS.map(d => ({ ...d, id: uid(), created: new Date().toISOString() }));
    tools = tools.map(t => this.normalize(t));
    this.setState({ tools });
    this.timer = setInterval(() => this.setState(s => ({ tick: s.tick + 1 })), 30000);
    this.onKey = e => {
      if (e.key === 'Escape' && this.state.modal) this.close();
      if (e.key === 'Enter' && this.state.modal && e.target.tagName !== 'TEXTAREA') this.save();
    };
    document.addEventListener('keydown', this.onKey);
  }

  componentWillUnmount() { clearInterval(this.timer); document.removeEventListener('keydown', this.onKey); this._fileHandle = null; }

  normalize(t) {
    const r = t.reset || {};
    const e = t.expiry || {};
    return {
      id: t.id || uid(), name: t.name || '未命名', provider: t.provider || '', category: t.category || 'chat',
      reset: { period: r.period || 'weekly', day: r.day != null ? parseInt(r.day) : 1, hour: parseInt(r.hour) || 0, minute: parseInt(r.minute) || 0 },
      expiry: { period: e.period || 'monthly', day: e.day != null ? parseInt(e.day) : 7 },
      quotaPct: t.quotaPct != null && t.quotaPct !== '' ? parseFloat(t.quotaPct) : null,
      created: t.created || new Date().toISOString()
    };
  }

  async persist(tools) {
    try {
      if (this._fileHandle) {
        const writable = await this._fileHandle.createWritable();
        await writable.write(JSON.stringify(tools, null, 2));
        await writable.close();
        return;
      }
    } catch (e) {}
    localStorage.setItem(KEY, JSON.stringify(tools));
  }
  async saveToFile() {
    try {
      if (window.showSaveFilePicker) {
        const handle = await window.showSaveFilePicker({
          suggestedName: 'ai-tools-data.json',
          types: [{ description: 'JSON文件', accept: { 'application/json': ['.json'] } }]
        });
        this._fileHandle = handle;
        const writable = await handle.createWritable();
        await writable.write(JSON.stringify(this.state.tools, null, 2));
        await writable.close();
        this.toast('✓ 已保存到文件');
        return;
      }
    } catch (e) { if (e.name !== 'AbortError') this.toast('✕ 保存失败'); return; }
    this.toast('提示：请先生成数据文件');
  }
  async loadFromFile() {
    try {
      if (window.showOpenFilePicker) {
        const [handle] = await window.showOpenFilePicker({
          types: [{ description: 'JSON文件', accept: { 'application/json': ['.json'] } }],
          multiple: false
        });
        this._fileHandle = handle;
        const file = await handle.getFile();
        const text = await file.text();
        if (text) {
          const data = JSON.parse(text);
          if (Array.isArray(data)) {
            const tools = data.map(t => this.normalize(t));
            this.update(tools);
            this.toast('✓ 已加载 ' + tools.length + ' 条');
            return;
          }
        }
        throw new Error('格式错误');
      }
    } catch (e) {
      if (e.name !== 'AbortError') this.toast('✕ 加载失败：' + e.message);
    }
  }
  update(tools) { this.persist(tools); this.setState({ tools }); }

  toast(msg) {
    const id = uid();
    this.setState(s => ({ toasts: [...s.toasts, { id, msg }] }));
    setTimeout(() => this.setState(s => ({ toasts: s.toasts.filter(t => t.id !== id) })), 2600);
  }

  nextDate(spec) {
    if (!spec || spec.day == null || isNaN(spec.day)) return null;
    const now = new Date();
    const h = spec.hour || 0, m = spec.minute || 0;
    if (spec.period === 'monthly') {
      let next = new Date(now.getFullYear(), now.getMonth(), spec.day, h, m, 0, 0);
      if (next <= now) next = new Date(now.getFullYear(), now.getMonth() + 1, spec.day, h, m, 0, 0);
      return next;
    }
    let diff = (parseInt(spec.day) - now.getDay() + 7) % 7;
    const next = new Date(now);
    next.setDate(next.getDate() + diff);
    next.setHours(h, m, 0, 0);
    if (next <= now) next.setDate(next.getDate() + 7);
    return next;
  }

  rel(date) {
    if (!date) return { text: '—', hours: null };
    const ms = date - new Date();
    const hours = ms / 3600000;
    const d = Math.floor(hours / 24);
    const h = Math.floor(hours % 24);
    if (d >= 1) return { text: h > 0 ? d + ' 天 ' + h + ' 时' : d + ' 天', hours };
    if (hours >= 1) return { text: Math.floor(hours) + ' 小时', hours };
    return { text: Math.max(Math.floor(ms / 60000), 0) + ' 分钟', hours };
  }

  fmt(date, withTime) {
    if (!date) return '—';
    const md = (date.getMonth() + 1) + '/' + date.getDate();
    const wd = WEEK[date.getDay()];
    if (!withTime) return md + ' ' + wd;
    const t = String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0');
    return md + ' ' + wd + ' ' + t;
  }

  markOf(t) {
    const hay = ((t.provider || '') + ' ' + (t.name || '')).toLowerCase();
    const brand = BRANDS.find(b => b.keys.some(k => hay.includes(k)));
    const p = (t.provider || t.name || '?').trim();
    const ch = p[0] || '?';
    return {
      mark: /[a-z]/i.test(ch) ? ch.toUpperCase() : ch,
      color: brand ? brand.color : '#7b8095',
      path: brand ? brand.path : null
    };
  }

  view(t) {
    const accent = this.props.accentColor || '#8b7cf6';
    const rd = this.nextDate(t.reset), ed = this.nextDate(t.expiry);
    const rr = this.rel(rd), er = this.rel(ed);
    const resetSoon = rr.hours != null && rr.hours <= 48;
    const expirySoon = er.hours != null && er.hours <= 24 * 7;
    const { mark, color, path } = this.markOf(t);
    return {
      t, resetDate: rd, resetHours: rr.hours, expiryHours: er.hours,
      resetSoon, expirySoon, mark, markColor: color,
      iconPath: path, hasIcon: !!path, noIcon: !path,
      resetRel: rr.text, resetWhen: this.fmt(rd, true),
      expiryWhen: this.fmt(ed, false), expiryRel: er.text === '—' ? '' : '剩 ' + er.text.split(' ').slice(0, 2).join(' '),
      resetColor: resetSoon ? accent : '#e9eaf0',
      expiryColor: expirySoon ? '#f5a524' : '#9296a6',
      statusColor: expirySoon ? '#f5a524' : resetSoon ? accent : '#2f3444'
    };
  }

  matchFilter(v, f) {
    if (f === 'all') return true;
    if (f === 'reset') return v.resetHours != null && v.resetHours <= 72;
    if (f === 'warning') return v.expirySoon;
    if (f === 'quota') return v.t.quotaPct != null && v.t.quotaPct >= 70;
    if (f === 'ok') return !v.expirySoon && !v.resetSoon;
    return true;
  }

  open(id) {
    if (!id) return this.setState({ modal: true, editId: null, form: this.blankForm(), brand: '__custom__' });
    const t = this.state.tools.find(x => x.id === id);
    if (!t) return;
    const form = {
      name: t.name, provider: t.provider, category: t.category,
      resetPeriod: t.reset.period, resetDay: String(t.reset.day),
      resetTime: String(t.reset.hour).padStart(2, '0') + ':' + String(t.reset.minute).padStart(2, '0'),
      expiryPeriod: t.expiry.period, expiryDay: String(t.expiry.day),
      quotaPct: t.quotaPct != null ? String(t.quotaPct) : ''
    };
    this.setState({ modal: true, editId: id, form, brand: this.detectBrand(form) });
  }

  pickBrand(id) {
    const def = this.BRAND_GRID.find(b => b.id === id);
    if (!def) return;
    this.setState(s => {
      const form = { ...s.form };
      if (id === '__custom__') {
        // 自定义：清空让用户填
        form.name = '';
        form.provider = '';
      } else {
        form.name = def.label;
        form.provider = def.provider;
      }
      return { brand: id, form };
    });
  }

  close() { this.setState({ modal: false }); }

  save() {
    const f = this.state.form;
    if (!f.name.trim()) return this.toast('⚠ 请输入工具名称');
    const [h, m] = (f.resetTime || '00:00').split(':');
    const data = this.normalize({
      id: this.state.editId, name: f.name.trim(), provider: f.provider.trim(), category: f.category,
      reset: { period: f.resetPeriod, day: f.resetDay, hour: h, minute: m },
      expiry: { period: f.expiryPeriod, day: f.expiryDay },
      quotaPct: f.quotaPct === '' ? null : f.quotaPct
    });
    let tools;
    if (this.state.editId) {
      tools = this.state.tools.map(t => t.id === this.state.editId ? { ...data, created: t.created } : t);
      this.toast('✓ 已更新');
    } else {
      tools = [data, ...this.state.tools];
      this.toast('✓ 已添加');
    }
    this.persist(tools);
    this.setState({ tools, modal: false });
  }

  dayOptions(period) {
    if (period === 'weekly') return WEEK.map((d, i) => ({ value: String(i), label: d }));
    return Array.from({ length: 31 }, (_, i) => ({ value: String(i + 1), label: (i + 1) + ' 日' }));
  }

  field(k) {
    return e => {
      const v = e.target.value;
      this.setState(s => {
        const form = { ...s.form, [k]: v };
        if (k === 'resetPeriod') form.resetDay = v === 'weekly' ? '1' : '1';
        if (k === 'expiryPeriod') form.expiryDay = v === 'weekly' ? '1' : '7';
        return { form };
      });
    };
  }

  renderVals() {
    const accent = this.props.accentColor || '#8b7cf6';
    const compact = (this.props.density || 'comfortable') === 'compact';
    const views = this.state.tools.map(t => this.view(t));
    const q = this.state.query.trim().toLowerCase();
    const rows = views
      .filter(v => !q || v.t.name.toLowerCase().includes(q) || (v.t.provider || '').toLowerCase().includes(q))
      .filter(v => this.matchFilter(v, this.state.filter))
      .sort((a, b) => (a.resetDate ? a.resetDate.getTime() : Infinity) - (b.resetDate ? b.resetDate.getTime() : Infinity))
      .map(v => ({
        ...v, name: v.t.name, provider: v.t.provider || '—',
        hasQuota: v.t.quotaPct != null, noQuota: v.t.quotaPct == null,
        quotaLabel: v.t.quotaPct != null ? v.t.quotaPct.toFixed(1) + '%' : '',
        quotaWidth: Math.max(Math.min(v.t.quotaPct || 0, 100), 1.5) + '%',
        quotaColor: (v.t.quotaPct || 0) > 80 ? '#ff6b6b' : (v.t.quotaPct || 0) > 55 ? '#f5a524' : '#3ecfb2',
        onEdit: () => this.open(v.t.id),
        onDelete: () => {
          if (!confirm('确定删除「' + v.t.name + '」？')) return;
          const tools = this.state.tools.filter(x => x.id !== v.t.id);
          this.update(tools); this.toast('✓ 已删除');
        },
        onQuota: () => {
          const cur = v.t.quotaPct != null ? v.t.quotaPct : '';
          const input = prompt('「' + v.t.name + '」已用额度百分比 (0–100)', cur);
          if (input === null) return;
          const val = input.trim() === '' ? null : parseFloat(input);
          if (val !== null && (isNaN(val) || val < 0 || val > 100)) return this.toast('⚠ 请输入 0–100');
          this.update(this.state.tools.map(x => x.id === v.t.id ? { ...x, quotaPct: val } : x));
          this.toast('✓ 额度已更新');
        }
      }));

    const hero = views.slice().sort((a, b) => (a.resetDate ? a.resetDate.getTime() : Infinity) - (b.resetDate ? b.resetDate.getTime() : Infinity))[0];
    const heroParts = hero ? hero.resetRel.split(' ') : [];
    const expiredSoon = views.filter(v => v.expirySoon).length;
    const resetting = views.filter(v => v.resetHours != null && v.resetHours <= 72).length;
    const heavy = views.filter(v => v.t.quotaPct != null && v.t.quotaPct >= 70).length;

    const chipDefs = [['all', '全部'], ['reset', '即将重置'], ['warning', '即将到期'], ['quota', '额度紧张'], ['ok', '正常']];

    return {
      accent,
      accentGlow: accent + '2e',
      showHero: this.props.showHero !== false && views.length > 0,
      rowPad: compact ? '12px 18px' : '18px 20px',
      query: this.state.query,
      onSearch: e => this.setState({ query: e.target.value }),
      chips: chipDefs.map(([id, label]) => ({
        id, label,
        bg: this.state.filter === id ? accent : 'transparent',
        fg: this.state.filter === id ? '#0c0d11' : '#9296a6',
        onClick: () => this.setState({ filter: id })
      })),
      stats: [
        { label: '订阅总数', value: String(views.length), unit: '个', color: '#e9eaf0' },
        { label: '72h 内重置', value: String(resetting), unit: '个', color: accent },
        { label: '7 天内到期', value: String(expiredSoon), unit: '个', color: expiredSoon ? '#f5a524' : '#3ecfb2' },
        { label: '额度 ≥70%', value: String(heavy), unit: '个', color: heavy ? '#ff6b6b' : '#3ecfb2' }
      ],
      heroValue: heroParts[0] || '—',
      heroUnit: hero ? hero.resetRel.replace(heroParts[0], '').trim() + ' 后重置' : '',
      heroName: hero ? hero.t.name : '暂无数据',
      heroMark: hero ? hero.mark : '·',
      heroMarkColor: hero ? hero.markColor : '#3a4054',
      heroIconPath: hero ? hero.iconPath : null,
      heroHasIcon: !!(hero && hero.iconPath),
      heroNoIcon: !(hero && hero.iconPath),
      heroWhen: hero ? hero.resetWhen : '',
      rows,
      isEmpty: rows.length === 0,
      emptyTitle: this.state.tools.length === 0 ? '还没有添加工具' : '没有匹配的结果',
      emptyHint: this.state.tools.length === 0 ? '点击右上角「添加工具」开始记录' : '换个关键词或筛选条件试试',
      modalOpen: this.state.modal,
      modalTitle: this.state.editId ? '编辑工具' : '添加工具',
      form: this.state.form,
      brandGrid: this.BRAND_GRID,
      brandSelected: this.state.brand || '__custom__',
      onPickBrand: id => this.pickBrand(id),
      resetDayOptions: this.dayOptions(this.state.form.resetPeriod),
      expiryDayOptions: this.dayOptions(this.state.form.expiryPeriod),
      onField: { name: this.field('name'), provider: this.field('provider'), category: this.field('category'), resetPeriod: this.field('resetPeriod'), resetDay: this.field('resetDay'), resetTime: this.field('resetTime'), expiryPeriod: this.field('expiryPeriod'), expiryDay: this.field('expiryDay'), quotaPct: this.field('quotaPct') },
      onAdd: () => this.open(null),
      onClose: () => this.close(),
      onSave: () => this.save(),
      onOverlayClick: () => this.close(),
      stop: e => e.stopPropagation(),
      toasts: this.state.toasts,
      fileRef: this.fileRef,
      onImportClick: () => this.fileRef && this.fileRef.current && this.fileRef.current.click(),
      onImportFile: e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
          try {
            const data = JSON.parse(ev.target.result);
            if (!Array.isArray(data)) throw new Error('格式错误');
            const tools = data.map(t => this.normalize(t));
            this.update(tools);
            this.toast('✓ 已导入 ' + tools.length + ' 条');
          } catch (err) { this.toast('✕ 导入失败：' + err.message); }
        };
        reader.readAsText(file);
        e.target.value = '';
      },
      onSaveToFile: () => this.saveToFile(),
      onLoadFromFile: () => this.loadFromFile(),
      onExport: () => {
        const blob = new Blob([JSON.stringify(this.state.tools, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'ai-tools-' + new Date().toISOString().slice(0, 10) + '.json';
        a.click();
        URL.revokeObjectURL(a.href);
        this.toast('✓ 已导出');
      },
      onResetDefaults: () => {
        if (!confirm('恢复默认示例数据？当前记录将被覆盖。')) return;
        this.update(DEFAULTS.map(d => this.normalize({ ...d, id: uid() })));
        this.toast('✓ 已恢复默认数据');
      }
    };
  }
}
