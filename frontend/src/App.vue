<template>
  <div id="app" class="v01">
    <div v-if="isMobile" class="mobile-restriction">
      <p>{{ $t('mobile') }}</p>
    </div>
    <div v-else class="row">
      <div class="column_one">
        <div class="column">
          <button class="flex-row-center-center class-___" @click="goToTelegramBot">
            <img src="/images/img_clock.svg" alt="Clock" class="clock" />
            <span>{{ $t('back_to_bot') }}</span>
          </button>
          <p class="validator ui text size-textlg">{{ $t('validator_launcher') }}</p>
        </div>
        <div class="container">
          <div v-if="isValidatingLink" class="loading-overlay">
            <div class="spinner"></div>
            <p>{{ $t('validating_link') }}</p>
          </div>
          <div v-else>
            <div v-if="!isLinkValid" class="error-message">
              <p class="flex-row-center-center class-__">{{ $t('validated_link_error') }}</p>
            </div>
            <div v-else>
              <div v-if="isLoading || isConnectingWallet" class="loading-overlay">
                <div class="spinner"></div>
                <p v-if="isLoading">{{ $t('sending_transaction') }}</p>
                <p v-else-if="isConnectingWallet">{{ $t('connecting_wallet') }}</p>
              </div>
              <div class="validator-container" v-if="currentValidator">
                <div v-if="currentValidatorIndex > 0" class="redelegate-message">
                  <p class="flex-row-center-center class-__"> {{ $t('redelegate_to_developers') }}</p>
                </div>
                <ValidatorCard :validator="currentValidator" @redelegate="handleRedelegate" />
              </div>
              <div v-else class="completion-message">
                <p class="flex-row-center-center class-__"><strong>{{ $t('thanks') }}</strong></p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <img src="/images/img_leonardo_phoeni.png" alt="Leonardophoeni" class="leonardophoeni" />
    </div>
  </div>
</template>

<script>
import ValidatorCard from './components/ValidatorCard.vue';
import {
  connectSigningClient,
  signAndBroadcast,
} from './utils/SigningClient.js';

export default {
  name: 'App',
  components: {
    ValidatorCard,
  },
  data() {
    return {
      validators: [],
      signingClient: null,
      account: null,
      currentNetwork: null,
      isLoading: false,
      isConnectingWallet: false,
      encodedUserId: '',
      encodedReferrerId: '',
      linkId: '',
      isLinkValid: false,
      isValidatingLink: true,
      errorMessage: '',
      currentValidatorIndex: 0,
      telegramBotLink: process.env.VUE_APP_TELEGRAM_BOT_LINK,
      backendUrl: '',
      isMobile: false,
    };
  },
  computed: {
    currentValidator() {
      return this.validators[this.currentValidatorIndex];
    },
  },
  async mounted() {
    document.title = "raptor";
    this.checkDevice();
    window.addEventListener('keplr_keystorechange', this.handleKeplrAccountChange);
    await this.extractParamsFromUrl();
    await this.fetchValidators();
    this.isValidatingLink = false;
  },
  methods: {
    setLocale(lang) {
      if (['en', 'ru'].includes(lang)) {
        this.$i18n.locale = lang;
        console.log(`Locale set to: ${lang}`);
      } else {
        this.$i18n.locale = 'en';
        console.log('Locale set to default: en');
      }
    },
    checkDevice() {
      const userAgent = navigator.userAgent.toLowerCase();
      this.isMobile = /android|iphone|ipad/.test(userAgent);
    },
    goToTelegramBot() {
      window.open(this.telegramBotLink, '_blank');
    },
    handleKeplrAccountChange() {
      this.signingClient = null;
      this.account = null;
    },
    async fetchValidators() {
      try {
        const response = await fetch('/validators.json');
        if (response.ok) {
          this.validators = await response.json();
        } else {
          throw new Error('Failed to load validator data.');
        }
      } catch (error) {
        this.errorMessage = 'Failed to load validator data.';
        console.error('Failed to load validator data:', error);
      }
    },
    async extractParamsFromUrl() {
      const params = new URLSearchParams(window.location.search);
      this.linkId = params.get('link_id') || '';
      this.encodedReferrerId = params.get('r_id') || '';
      this.encodedUserId = params.get('u_id') || '';
      const lang = params.get('lang') || 'en';

      this.setLocale(lang);

      if (!this.encodedReferrerId || !this.encodedUserId || !this.linkId) {
        this.errorMessage = 'Access denied. Invalid or missing referral link parameters.';
        console.error('Missing parameters in URL.');
        return;
      }
      await this.validateLink();
    },
    async validateLink() {
      try {
        const response = await fetch(`${this.backendUrl}/api/check_link`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            u_id: this.encodedUserId,
            r_id: this.encodedReferrerId,
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
      this.isConnectingWallet = true;
      try {
        const { client, account } = await connectSigningClient(
          network,
          rpcUrl,
          gasPrice
        );
        this.signingClient = client;
        this.account = account;
        this.currentNetwork = network;
        alert(
          this.$t('connected_message', {
            address: this.account.address,
            network: this.currentNetwork,
          })
        );
        return true;
      } catch (error) {
        console.error('Failed to connect Keplr:', error);
        alert(this.$t('failed_to_connect_keplr', { error: error.message }));
        return false;
      } finally {
        this.isConnectingWallet = false;
      }
    },
    async handleRedelegate(validator) {
      const rpcUrl = {
        celestia: process.env.VUE_APP_CELESTIA_RPC_URL,
        'fetchhub-4': process.env.VUE_APP_FETCH_RPC_URL,
      };
      const isConnected = await this.connectKeplr(
        validator.network,
        rpcUrl[validator.network],
        validator.gasPrice
      );
      if (!isConnected) {
        return;
      }

      try {
        this.isLoading = true;
        const memo =
          validator.memoDev +
          this.encodedReferrerId +
          validator.memoVal +
          this.encodedUserId +
          validator.memoChain;

        const result = await signAndBroadcast(
          this.signingClient,
          this.account,
          validator.address,
          validator.validatorValoper,
          validator.feeDenom,
          validator.feeAmount,
          memo
        );

        if (result.code === 0) {
          const transactionHash = result.transactionHash;

          await this.sendTransactionDataToBackend(
            this.backendUrl + validator.postUrl,
            this.account.address,
            transactionHash,
            ''
          );

          alert(this.$t('transaction_success', { hash: transactionHash }));

          this.currentValidatorIndex += 1;
        } else {
          console.log(result);
          throw new Error(result.rawLog);
        }
      } catch (error) {
        console.error('Failed to send redelegate transaction:', error);
        await this.sendTransactionDataToBackend(
          this.backendUrl + validator.postUrl,
          this.account.address,
          '',
          error.message
        );
        alert(this.$t('redelegate_failed', { error: error.message }));
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
            u_id: this.encodedUserId,
            address: address,
            tx: txHash,
            tx_error: txError,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to save data on the backend');
        }
      } catch (error) {
        console.error('Error sending data to backend:', error);
        throw error;
      }
    },
  },
};
</script>

<style scoped>
@import './assets/styles.css';
@import './assets/components.css';
@import './assets/V01.css';
@import './assets/index.css';

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 19, 43, 0.8);
  display: flex;
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

.mobile-restriction {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #0f132b;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.5rem;
  z-index: 2000;
  text-align: center;
}
</style>
