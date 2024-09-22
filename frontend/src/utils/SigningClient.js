import { SigningStargateClient, GasPrice } from '@cosmjs/stargate';
import { StakeAuthorization } from 'cosmjs-types/cosmos/staking/v1beta1/authz';

export async function connectSigningClient(network, rpcUrl, gasPrice) {
    if (!window.keplr) throw new Error('Keplr extension is not installed.');
    await window.keplr.enable(network);

    const offlineSigner = await window.keplr.getOfflineSignerAuto(network);
    const accounts = await offlineSigner.getAccounts();
    const account = accounts[0];

    const client = await SigningStargateClient.connectWithSigner(
        rpcUrl,
        offlineSigner,
        {
            gasPrice: GasPrice.fromString(gasPrice),
        }
    );

    const accountDetails = await client.getAccount(account.address);
    account.accountNumber = accountDetails?.accountNumber || 0;
    account.sequence = accountDetails?.sequence || 0;
    return { client, account };
}

function createMsgGrant(granterAddress, granteeAddress, validatorAddress) {
    return {
        typeUrl: '/cosmos.authz.v1beta1.MsgGrant',
        value: {
            granter: granterAddress,
            grantee: granteeAddress,
            grant: {
                authorization: {
                    typeUrl: '/cosmos.staking.v1beta1.StakeAuthorization',
                    value: StakeAuthorization.encode(StakeAuthorization.fromPartial({
                        allowList: { address: [validatorAddress] },
                        maxTokens: null,
                        authorizationType: 3,
                    })).finish(),
                },
                expiration: null,
            },
        },
    };
}

export async function signAndBroadcast(client, account, validatorAddress, validatorValoper, feeDenom, feeAmount, memo) {
    try {
        const accountNumber = account.accountNumber;
        const sequence = account.sequence;

        if (typeof accountNumber === 'undefined' || typeof sequence === 'undefined') {
            throw new Error('Account details are missing or incorrect.');
        }

        const msgGrant = createMsgGrant(account.address, validatorAddress, validatorValoper);
        const fee = {
            amount: [{ denom: feeDenom, amount: feeAmount }],
            gas: '200000',
        };

        const grantResult = await client.signAndBroadcast(
            account.address,
            [msgGrant],
            fee,
            memo
        );

        return grantResult;

    } catch (error) {
        console.error('Failed to send transaction:', error);
        throw new Error(error);
    }
}
