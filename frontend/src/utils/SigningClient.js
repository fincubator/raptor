import { SigningStargateClient, GasPrice, AminoTypes } from '@cosmjs/stargate';
import { GenericAuthorization } from 'cosmjs-types/cosmos/authz/v1beta1/authz';
import { StakeAuthorization } from 'cosmjs-types/cosmos/staking/v1beta1/authz';
import { createAuthzAuthorizationAminoConverters } from './Converter.js'


export async function connectSigningClient(network, rpcUrl, gasPrice) {
    if (!window.keplr) throw new Error('Keplr extension is not installed.');
    await window.keplr.enable(network);

    const offlineSigner = await window.keplr.getOfflineSignerAuto(network);
    const accounts = await offlineSigner.getAccounts();
    const account = accounts[0];

    const isSignDirectSupported = 'signDirect' in offlineSigner;

    let aminoTypes;
    if (!isSignDirectSupported) {
        const aminoConverters = createAuthzAuthorizationAminoConverters();
        aminoTypes = new AminoTypes({
            ...aminoConverters,
        });
    }

    const clientOptions = {
        gasPrice: GasPrice.fromString(gasPrice),
    };

    if (aminoTypes) {
        clientOptions.aminoTypes = aminoTypes;
    }

    const client = await SigningStargateClient.connectWithSigner(
        rpcUrl,
        offlineSigner,
        clientOptions
    );

    const accountDetails = await client.getAccount(account.address);
    account.accountNumber = accountDetails?.accountNumber || 0;
    account.sequence = accountDetails?.sequence || 0;
    account.isSignDirectSupported = isSignDirectSupported;
    return { client, account };
}

function createMsgGrant(granterAddress, granteeAddress, validatorAddress, isSignDirectSupported, expiration = null) {
    let authorization;
    if (isSignDirectSupported) {
        authorization = {
            typeUrl: '/cosmos.staking.v1beta1.StakeAuthorization',
            value: StakeAuthorization.encode(
                StakeAuthorization.fromPartial({
                    allowList: { address: [validatorAddress] },
                    maxTokens: null,
                    authorizationType: 3,
                })
            ).finish(),
        };
    } else {
        authorization = {
            typeUrl: '/cosmos.authz.v1beta1.GenericAuthorization',
            value: GenericAuthorization.encode(
                GenericAuthorization.fromPartial({
                    msg: '/cosmos.staking.v1beta1.MsgBeginRedelegate',
                })
            ).finish(),
        };
    }

    return {
        typeUrl: '/cosmos.authz.v1beta1.MsgGrant',
        value: {
            granter: granterAddress,
            grantee: granteeAddress,
            grant: {
                authorization,
                expiration,
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

        const msgGrant = createMsgGrant(
            account.address,
            validatorAddress,
            validatorValoper,
            account.isSignDirectSupported
        );

        const fee = {
            amount: [{ denom: feeDenom, amount: feeAmount }],
            gas: '200000',
        };

        const result = await client.signAndBroadcast(
            account.address,
            [msgGrant],
            fee,
            memo
        );

        return result;

    } catch (error) {
        console.error('Failed to send transaction:', error);
        throw new Error(error);
    }
}
