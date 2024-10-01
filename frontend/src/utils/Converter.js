import { MsgGrant } from 'cosmjs-types/cosmos/authz/v1beta1/tx';
import { GenericAuthorization } from 'cosmjs-types/cosmos/authz/v1beta1/authz';
import { Timestamp } from 'cosmjs-types/google/protobuf/timestamp';
import Long from 'long';

export function createAuthzAuthorizationAminoConverters() {
  return {
    '/cosmos.authz.v1beta1.MsgGrant': {
      aminoType: 'cosmos-sdk/MsgGrant',
      toAmino: ({ granter, grantee, grant }) => {
        if (!grant || !grant.authorization) {
          throw new Error(`Unsupported grant type: '${grant?.authorization?.typeUrl}'`);
        }
        let authorizationValue;
        switch (grant.authorization.typeUrl) {
          case '/cosmos.authz.v1beta1.GenericAuthorization': {
            const generic = GenericAuthorization.decode(grant.authorization.value);
            authorizationValue = {
              type: 'cosmos-sdk/GenericAuthorization',
              value: {
                msg: generic.msg,
              },
            };
            break;
          }
          default:
            throw new Error(`Unsupported grant type: '${grant.authorization.typeUrl}'`);
        }
        const expiration = grant.expiration
          ? new Date(
              grant.expiration.seconds.toNumber() * 1000 +
                grant.expiration.nanos / 1e6,
            )
              .toISOString()
              .replace(/\.000Z$/, 'Z')
          : undefined;
        return {
          granter,
          grantee,
          grant: {
            authorization: authorizationValue,
            expiration,
          },
        };
      },
      fromAmino: ({ granter, grantee, grant }) => {
        const authorizationType = grant.authorization.type;
        let authorizationValue;
        switch (authorizationType) {
          case 'cosmos-sdk/GenericAuthorization': {
            authorizationValue = {
              typeUrl: '/cosmos.authz.v1beta1.GenericAuthorization',
              value: GenericAuthorization.encode({
                msg: grant.authorization.value.msg,
              }).finish(),
            };
            break;
          }
          default:
            throw new Error(`Unsupported grant type: '${grant.authorization.type}'`);
        }
        const expiration = grant.expiration
          ? Timestamp.fromPartial({
              seconds: Long.fromNumber(Math.floor(Date.parse(grant.expiration) / 1000)),
              nanos: (Date.parse(grant.expiration) % 1000) * 1e6,
            })
          : undefined;
        return MsgGrant.fromPartial({
          granter,
          grantee,
          grant: {
            authorization: authorizationValue,
            expiration,
          },
        });
      },
    },
    '/cosmos.authz.v1beta1.GenericAuthorization': {
      aminoType: 'cosmos-sdk/GenericAuthorization',
      toAmino: ({ msg }) => {
        return { msg };
      },
      fromAmino: ({ msg }) => {
        return GenericAuthorization.fromPartial({ msg });
      },
    },
  };
}