const Web3 = require("web3");
const commander = require('commander');

const aggregatorV3InterfaceABI = [{
    "inputs":[],
    "name":"decimals",
    "outputs":[{"internalType":"uint8","name":"","type":"uint8"}],
    "stateMutability":"view",
    "type":"function"
},{
    "inputs":[],
    "name":"description",
    "outputs":[{"internalType":"string","name":"","type":"string"}],
    "stateMutability":"view",
    "type":"function"
},{
    "inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],
    "name":"getRoundData",
    "outputs":[
        {"internalType":"uint80","name":"roundId","type":"uint80"},
        {"internalType":"int256","name":"answer","type":"int256"},
        {"internalType":"uint256","name":"startedAt","type":"uint256"},
        {"internalType":"uint256","name":"updatedAt","type":"uint256"},
        {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
    ],
    "stateMutability":"view",
    "type":"function"
},{
    "inputs":[],
    "name":"latestRoundData",
    "outputs":[
        {"internalType":"uint80","name":"roundId","type":"uint80"},
        {"internalType":"int256","name":"answer","type":"int256"},
        {"internalType":"uint256","name":"startedAt","type":"uint256"},
        {"internalType":"uint256","name":"updatedAt","type":"uint256"},
        {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
    ],
    "stateMutability":"view",
    "type":"function"
},{
    "inputs":[],
    "name":"version",
    "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
    "stateMutability":"view",
    "type":"function"
}]

commander
  .usage('[OPTIONS]...')
  .option('-b, --batch <value>', 'Batch size.', 100)
  .option('-i, --iterations <value>', 'Number of iterations.', 5)
  .option('-c, --contract <value>', 'Contract address', '0x83441C3A10F4D05de6e0f2E849A850Ccf27E6fa7')
  .option('-r, --rpc <value>', 'RPCs', [
        'https://rpc.ankr.com/eth',
        'https://cloudflare-eth.com',
        'https://eth-mainnet.public.blastapi.io',
        'https://eth-rpc.gateway.pokt.network',
        'https://api.securerpc.com/v1'
    ])
  .parse(process.argv);

function batch(iteration, batch_size, contract, rpcs) {
    console.log(`Starting iteration ${iteration}`);
    let iteration_msg = `Iteration ${iteration} took`;
    console.time(iteration_msg);
    let promises = []
    for (let i=0; i< batch_size; i++) {
        let rpc_index = i % rpcs.length;
        let rpc = rpcs[rpc_index];
        const web3 = new Web3(rpc)
        const priceFeed = new web3.eth.Contract(aggregatorV3InterfaceABI, contract)
        let start = Date.now()
        let promise = priceFeed.methods.latestRoundData().call()
            .then((round_data) => {
                let usd_price = round_data[1] / 100_000_000
                let end = Date.now()
                let duration =  Math.abs(end - start);
                console.log(`${iteration}.${i}:\t ${duration}ms\t${usd_price} USD\tRPC: ${rpc}`);
            })
            .catch((e) => {
                console.error(`${iteration}.${i}:\tRPC: ${rpc}\tError:${e.message}`);
            });
        promises.push(promise)
    }
    return Promise.all(promises)
        .then(results => {
            console.timeEnd(iteration_msg);
        })
}

function setIntervalLimited(callback, interval, x) {
    for (var i = 0; i < x; i++) {
        setTimeout(callback, i * interval);
    }
}

async function main() {
    const options = commander.opts();
    const batch_size = options.batch ;
    const iterations = options.iterations;
    const contract = options.contract;
    const rpcs = options.rpc;

    let promises  = [];
    let i = 0;
    setIntervalLimited(function() {
        promises.push(batch(i, batch_size, contract, rpcs));
        ++i;
    }, 1000, iterations)

    return Promise.resolve(promises)
        .catch(e => console.log)
}
    
if (require.main === module) {
    main();
}
      