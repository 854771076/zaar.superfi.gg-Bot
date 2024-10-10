const bip32 = require('bip32');
const bip39 = require('bip39');
const ecc = require('tiny-secp256k1');
const crypto = require('crypto');
const bitcoin = require('bitcoinjs-lib');
const {ECPairFactory} = require('ecpair');

bitcoin.initEccLib(ecc);
const network = bitcoin.networks.bitcoin;
const toXOnly = (pubKey) => pubKey.length === 32 ? pubKey : pubKey.slice(1, 33);

function create() {
    // 生成随机种子
    const randomSeed = crypto.randomBytes(32);
    // 通过随机种子生成根秘钥
    const root = bip32.BIP32Factory(ecc).fromSeed(randomSeed, network);
    // 定义路径
    const path = "m/86'/1'/0'/0/0";
    // 通过路径生成密钥对
    const childNode = root.derivePath(path);
    const keyPair = ECPairFactory(ecc).fromPrivateKey(childNode.privateKey, {network});
    const xOnlyPubkey = toXOnly(keyPair.publicKey);
    const {address, output} = bitcoin.payments.p2tr({internalPubkey: xOnlyPubkey, network});
    const WIF = keyPair.toWIF();
    // keyPairInstance
    return {address: address, WIF: WIF};
}

function getKeyPairByPrivateKey(privateKey) {
    return ECPairFactory(ecc).fromWIF(privateKey, network);
}

create()