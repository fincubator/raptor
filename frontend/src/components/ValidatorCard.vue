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
      <button type="submit" class="send_redelegate">Send Redelegate Authz</button>
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
@import '../assets/styles.css';
@import '../assets/components.css';
@import '../assets/V01.css';
@import '../assets/index.css';


</style>