<template>
  <div id="app">
    <header>
      <h1>Raptor</h1>
      <a href="https://t.me/ValidatorLauncherBot" target="_blank" class="telegram-btn">Telegram Bot</a>
    </header>

    <div class="container">
      <div v-if="isValidatingLink" class="loading-overlay">
        <div class="spinner"></div>
        <p>Validating link, please wait...</p>
      </div>

      <div v-else>
        <div v-if="!isLinkValid" class="error-message">
          <p>{{ errorMessage }}</p>
        </div>

        <div v-else>
          <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
            <p>Sending transaction, please wait...</p>
          </div>

          <div class="validator-list">
            <ValidatorCard
              v-for="(validator, index) in validators"
              :key="index"
              :validator="validator"
              @redelegate="handleRedelegate"
            />
          </div>
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
          logo: 'https://avatars.githubusercontent.com/u/108546933?s=200&v=4',
          name: 'POSTHUMAN',
          chain: 'Celestia Network (TIA)',
          stats: {
            commission: '5%',
          },
          address: 'celestia1zwjfxr3j9gnnrhxwtt8t6qqr4pdn7cgj33hd7c',
          validatorValoper: 'celestiavaloper1snun9qqk9eussvyhkqm03lz6f265ekhnnlw043',
          network: 'celestia',
          rpcUrl: 'https://celestia-rpc.stake-town.com',
          gasPrice: '0.025utia',
          feeDenom: 'utia',
          feeAmount: '10000',
          backendUrl: 'http://127.0.0.1:8000/api/tia',
        },
        {
          logo: 'https://avatars.githubusercontent.com/u/19353587?s=200&v=4',
          name: 'Finteh',
          chain: 'Fetch.ai Network (FET)',
          stats: {
            commission: '7%',
          },
          address: 'fetch1ujc2kt26d3a0x7v92e5acfu952j228f2cvkyay',
          validatorValoper: 'fetchvaloper1ujc2kt26d3a0x7v92e5acfu952j228f2agf8wr',
          network: 'fetchhub-4',
          rpcUrl: 'https://fetch-rpc.cosmosrescue.com',
          gasPrice: '0.025afet',
          feeDenom: 'afet',
          feeAmount: '10000',
          backendUrl: 'http://127.0.0.1:8000/api/fet',
        },
      ],
      signingClient: null,
      account: null,
      currentNetwork: null,
      isLoading: false,
      encodedUserId: '',
      encodedReferrerId: '',
      linkId: '',
      isLinkValid: false,
      isValidatingLink: true,
      errorMessage: '',
    };
  },
  async mounted() {
    await this.extractParamsFromUrl();
    this.isValidatingLink = false;
  },
  methods: {
    async extractParamsFromUrl() {
      const params = new URLSearchParams(window.location.search);
      this.encodedReferrerId = params.get('ref_id') || '';
      this.encodedUserId = params.get('user_id') || '';
      this.linkId = params.get('link_id') || '';

      if (!this.encodedReferrerId || !this.encodedUserId || !this.linkId) {
        this.errorMessage = 'Access denied. Invalid or missing referral link parameters.';
        console.error('Missing parameters in URL.');
        return;
      }
      await this.validateLink();
    },
    async validateLink() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/check_link', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: this.encodedUserId,
            ref_id: this.encodedReferrerId,
            link_id: this.linkId,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.valid) {
            this.isLinkValid = true;
          } else {
            this.errorMessage = data.message || 'Access denied. The link has already been used.';
            console.error('Link validation failed:', data.message);
          }
        } else {
          const errorData = await response.json();
          this.errorMessage = errorData.detail || 'Access denied. Invalid link.';
          console.error('Link validation failed:', errorData.detail);
        }
      } catch (error) {
        this.errorMessage = 'An error occurred while validating the link.';
        console.error('Error validating link:', error);
      }
    },
    async connectKeplr(network, rpcUrl, gasPrice) {
      if (this.currentNetwork === network && this.signingClient && this.account) {
        alert(`Already connected to ${network} network with address: ${this.account.address}`);
        return true;
      }
      try {
        const { client, account } = await connectSigningClient(network, rpcUrl, gasPrice);
        this.signingClient = client;
        this.account = account;
        this.currentNetwork = network;
        alert(`Connected with address: ${this.account.address} on ${network} network`);
        return true;
      } catch (error) {
        console.error('Failed to connect Keplr:', error);
        alert('Failed to connect Keplr. Please refresh the page and try again.');
        return false;
      }
    },
    async handleRedelegate(validator) {
      const isConnected = await this.connectKeplr(validator.network, validator.rpcUrl, validator.gasPrice);
      if (!isConnected) {
        return;
      }

      try {
        this.isLoading = true;

        const result = await signAndBroadcast(
          this.signingClient,
          this.account,
          validator.address,
          validator.validatorValoper,
          validator.feeDenom,
          validator.feeAmount
        );

        if (result.code === 0) {
          const transactionHash = result.transactionHash;

          await this.sendTransactionDataToBackend(
            validator.backendUrl,
            this.account.address,
            transactionHash,
            ''
          );

          alert(`Transaction successful! Hash: ${transactionHash}`);
        } else {
          console.log(result);
          throw new Error(result.rawLog);
        }
      } catch (error) {
        console.error('Failed to send redelegate transaction:', error);
        await this.sendTransactionDataToBackend(
          validator.backendUrl,
          this.account.address,
          '',
          error.message
        );
        alert('Failed to send redelegate transaction. Please refresh the page and try again.');
      } finally {
        this.isLoading = false;
      }
    },
    async sendTransactionDataToBackend(url, address, txHash, txError) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            telegram_id: this.encodedUserId,
            address: address,
            tx: txHash,
            tx_error: txError,
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
