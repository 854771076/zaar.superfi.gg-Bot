const wallet_1=require('@unisat/wallet-sdk/lib/wallet/estimate-wallet.js')
const network_1=require('@unisat/wallet-sdk/lib/network/index.js')
const types_1=require('@unisat/wallet-sdk/lib/types.js')
async function sign(wif,message,type='bip322-simple') {
    // 使用 WIF 导入私钥
    let wallet=new wallet_1.EstimateWallet(wif,network_1.NetworkType.MAINNET,types_1.AddressType.P2TR)
    let data=await wallet.signMessage(message,type=type)
    return data

}

// 从命令行获取参数
const wif = process.argv[2];
const message = process.argv[3];
const type = process.argv[4];

// 调用异步函数并处理结果
sign(wif, message, type)
.then((result) => {
    console.log(result);  // 输出结果
    process.exit(0);      // 正常退出
})
.catch((error) => {
    console.error(error);  // 输出错误
    process.exit(1);       // 非正常退出
});