const wallet_1=require('@unisat/wallet-sdk/lib/wallet/estimate-wallet.js')
const network_1=require('@unisat/wallet-sdk/lib/network/index.js')
const types_1=require('@unisat/wallet-sdk/lib/types.js')
async function sign(wif,message,type='bip322-simple') {
    // 使用 WIF 导入私钥
    let wallet=new wallet_1.EstimateWallet(wif,network_1.NetworkType.MAINNET,types_1.AddressType.P2TR)
    let data=await wallet.signMessage(message,type=type)
    return data

}
// AUAZgZl52s6am84kslAxge/4kzXcDuHHnE+bQuaAxfBOxKNQCw8S8S/7ZoYnrhP4mdSFJWD8Mu6lmVCuhJlCDEhw
// AUAZgZl52s6am84kslAxge/4kzXcDuHHnE+bQuaAxfBOxKNQCw8S8S/

// var e =sign('KxzuJfKMXrX8hK1JwPCcDimME3NcHZ5g9sTWFSfEjSLGYkZEuHk7','Address:\nbc1pt5y373ekqsuck0y8usell37dy8lms770lrrhg0x7s88288vz09eqa825ua\n\nNonce:\n42605c40a7795a853f274e1c9b48c0e05e5305a5457f1416a37dafaeafe7d19a\n\n')
// e.then((result) => {
//         console.log(result);  // 输出结果
//         process.exit(0);      // 正常退出
// })
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