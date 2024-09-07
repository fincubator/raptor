<template>
    <div class="validator-card">
      <img :src="validator.logo" alt="Validator Logo" class="validator-logo" />
      <div class="validator-name">{{ validator.name }}</div>
      <div class="validator-chain">{{ validator.chain }}</div>
      <div class="validator-stats">
        Voting Power: {{ validator.stats.votingPower }}<br />
        Commission: {{ validator.stats.commission }}<br />
        Uptime: {{ validator.stats.uptime }}
      </div>
      <form @submit.prevent="submitRedelegate" class="authz-form">
        <button type="submit">Send Redelegate Authz</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      validator: Object,
    },
    data() {
      return {
        maxTokens: '',
      };
    },
    methods: {
      submitRedelegate() {
        this.$emit('redelegate', this.validator, this.maxTokens);
      },
    },
  };
  </script>
  
  <style scoped>
  /* Add any additional styles here */
  </style>
  