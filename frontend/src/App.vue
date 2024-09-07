<template>
  <div id="app">
    <header>
      <h1>Raptor</h1>
      <a href="https://t.me/ValidatorLauncherBot" target="_blank" class="telegram-btn">Telegram Bot</a>
    </header>

    <div class="container">
      <div v-if="!hasReferralCode" class="error-message">
        <p>Access to the site is restricted without a referral code. Please contact the developers to obtain one.</p>
      </div>

      <div v-else>
        <div v-if="isLoading" class="loading-overlay">
          <div class="spinner"></div>
          <p>Sending transaction, please wait...</p>
        </div>

        <div class="validator-list">
          <ValidatorCard v-for="(validator, index) in validators" :key="index" :validator="validator"
            @redelegate="handleRedelegate" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ValidatorCard from './components/ValidatorCard.vue';
import { connectSigningClient, signAndBroadcast } from './utils/SigningClient.js';

export default {
  name: 'App',
  components: {
    ValidatorCard,
  },
  data() {
    return {
      validators: [
        {
          logo: 'https://example.com/posthuman-logo.png',
          name: 'POSTHUMAN',
          chain: 'Celestia Network (TIA)',
          stats: {
            votingPower: '2,345,678',
            commission: '5%',
            uptime: '99.99%',
          },
          address: 'celestia1zwjfxr3j9gnnrhxwtt8t6qqr4pdn7cgj33hd7c',
          network: 'celestia',
          rpcUrl: 'https://rpc.cosmos.directory/celestia',
          gasPrice: '0.025utia',
          feeDenom: 'utia',
          feeAmount: '10000',
          backendUrl: 'http://127.0.0.1:8000/api_tia',
        },
        {
          logo: 'https://example.com/finteh-logo.png',
          name: 'Finteh',
          chain: 'Fetch.ai Network (FET)',
          stats: {
            votingPower: '1,876,543',
            commission: '7%',
            uptime: '99.98%',
          },
          address: 'fetch....',
          network: 'fetchhub-4',
          rpcUrl: 'https://rpc.cosmos.directory/fetchhub',
          gasPrice: '0.025afet',
          feeDenom: 'afet',
          feeAmount: '10000',
          backendUrl: 'http://127.0.0.1:8000/api_fet',
        },
      ],
      signingClient: null,
      account: null,
      currentNetwork: null,
      isLoading: false,
      encodedTelegramId: '',
      encodedReferralCode: '',
      hasReferralCode: true,

    };
  },
  mounted() {
    this.extractParamsFromUrl();
  },
  methods: {
    extractParamsFromUrl() {
      const params = new URLSearchParams(window.location.search);
      this.encodedReferralCode = params.get('referral_code') || '';
      this.encodedTelegramId = params.get('id') || '';

      if (!this.encodedReferralCode || !this.encodedTelegramId) {
        this.hasReferralCode = false;
        console.error('Missing referral_code or id parameters in URL.');
        alert('Missing referral_code or id.');

      }
    },
    async connectKeplr(network, rpcUrl, gasPrice) {
      if (this.currentNetwork === network && this.signingClient && this.account) {
        alert(`Already connected to ${network} network with address: ${this.account.address}`);
        return;
      }
      try {
        const { client, account } = await connectSigningClient(network, rpcUrl, gasPrice);
        this.signingClient = client;
        this.account = account;
        this.currentNetwork = network;
        alert(`Connected with address: ${this.account.address} on ${network} network`);
      } catch (error) {
        console.error('Failed to connect Keplr:', error);
        alert('Failed to connect Keplr. Please кefresh the page page try again.');
      }
    },
    async handleRedelegate(validator) {
      try {
        await this.connectKeplr(validator.network, validator.rpcUrl, validator.gasPrice);
        console.log("this.accont", this.account)
        this.isLoading = true;
        const result = await signAndBroadcast(
          this.signingClient,
          this.account,
          validator.address,
          validator.feeDenom,
          validator.feeAmount
        );

        if (result.code === 0) {
          const transactionHash = result.transactionHash;
          await this.sendTransactionDataToBackend(
            validator.backendUrl,
            this.account.address,
            transactionHash
          );
          alert(`Transaction successful! Hash: ${result.transactionHash}`);
        } else {
          throw new Error(result.rawLog);
        }
      } catch (error) {
        console.error('Failed to send redelegate transaction:', error);
        alert('Failed to send redelegate transaction. Please кefresh the page page try again.');
      } finally {
        this.isLoading = false;
      }
    },
    async sendTransactionDataToBackend(url, address, txHash) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            telegram_id: this.encodedTelegramId,
            referral_inf_code: this.encodedReferralCode,
            address: address,
            tx: txHash,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to save data on the backend');
        }

        const data = await response.json();
        console.log('Data saved successfully:', data);
      } catch (error) {
        console.error('Error sending data to backend:', error);
        throw error;
      }
    },
  },
};
</script>

<style scoped>
@import './assets/style.css';

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  color: #fff;
}

.spinner {
  border: 8px solid rgba(255, 255, 255, 0.3);
  border-top: 8px solid #fff;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
