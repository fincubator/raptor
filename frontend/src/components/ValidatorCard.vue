<template>
  <div class="validator-card">
    <img :src="validator.logo" alt="Validator Logo" class="validator-logo" />
    <div class="validator-details">
      <div class="validator-name">{{ validator.name }}</div>
      <div class="validator-chain">{{ validator.chain }}</div>
      <div class="validator-stats">
        <p>Commission: {{ validator.stats.commission }}</p>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: validator.percents + '%' }"
            ></div>
          </div>
          <span class="progress-percents">{{ validator.percents }}% bonded</span>
        </div>

      </div>
    </div>
    <form @submit.prevent="submitRedelegate" class="authz-form">
      <button type="submit">Send Redelegate Authz</button>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    validator: {
      type: Object,
      required: true,
      validator(value) {
        return (
          typeof value.percents === 'number' &&
          value.percents >= 0 &&
          value.percents <= 100
        );
      },
    },
  },
  methods: {
    submitRedelegate() {
      this.$emit('redelegate', this.validator);
    },
  },
};
</script>

<style scoped>
.validator-card {
  border: 1px solid #464957;
  border-radius: 8px;
  padding: 16px;
  width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #222631;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.validator-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 16px;
}

.validator-details {
  width: 100%;
  text-align: center;
  margin-bottom: 16px;
}

.validator-name {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 4px;
}

.validator-chain {
  color: #918a8a;
  margin-bottom: 8px;
}

.validator-stats {
  font-size: 0.9em;
  color: #e0e0e0;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.progress-bar {
  flex: 1;
  height: 10px;
  background-color: #e0e0e0;
  overflow: hidden;
  margin-right: 8px;
}

.progress-fill {
  height: 100%;
  background-color: #8e44ad;
  transition: width 0.3s ease;
}

.progress-percents {
  font-size: 0.9em;
  color: #e0e0e0;
}

.authz-form {
  width: 100%;
  display: flex;
  justify-content: center;
}

.authz-form button {
  padding: 8px 16px;
  background-color: #0088cc;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.authz-form button:hover {
  background-color: #20aa27;
}
</style>
