<template>
  <div class="column-1">
    <div class="rowposthuman">
      <img :src="validator.logo" alt="Validator Logo" class="imageeight_one" />
      <div class="columnposthuman">
        <p class="posthuman ui text size-textmd">{{ validator.name }}</p>
        <p class="celestia ui text size-texts">{{ validator.chain }}</p>
        <p class="votingpower ui text size-texts">commission: {{ validator.commission }}</p>
        <p class="votingpower ui text size-texts">website: <a :href="validator.website" target="_blank">{{ validator.website }}</a></p>
      </div>
    </div>
    <form @submit.prevent="submitRedelegate" class="authz-form">
      <button type="submit" class="send_redelegate">{{ $t('send_redelegate_msg') }}</button>
      <button
        v-if="validator.name === 'finteh'"
        type="button"
        class="no_tokens_button"
        @click="handleNoTokens"
      >
        {{ $t('no_tokens_message', { chain: validator.chain }) }}
      </button>
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
    handleNoTokens() {
      this.$emit('no-tokens');
    },
  },
};
</script>

<style scoped>
@import '../assets/styles.css';
@import '../assets/components.css';
@import '../assets/V01.css';
@import '../assets/index.css';

.no_tokens_button {
  color: #fff;
  padding: 10px;
  margin-top: 15px;
  border: none;
  cursor: pointer;
}
.no_tokens_button:hover {
  text-decoration: underline;
}

</style>