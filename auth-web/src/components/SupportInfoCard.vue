<template>
  <v-card class="support-info-card">
    <v-card-title>Need Assistance?</v-card-title>
    <v-card-text>
      <p class="mb-0">
        For support or questions about this application, please contact us at:
      </p>
      <ul class="contact-info">
        <li class="contact-info__row">
          <span class="contact-info__type">Phone:</span>
          <span class="contact-info__value">{{ $t('techSupportPhone') }}</span>
        </li>
        <li class="contact-info__row">
          <span class="contact-info__type">Email:</span>
          <span class="contact-info__value"><a :href="'mailto:' + $t('techSupportEmail')">{{ $t('techSupportEmail') }}</a></span>
        </li>
      </ul>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'SupportInfoCard'
}
</script>

<style lang="scss" scoped>
  @import "../assets/scss/theme.scss";

  .v-card__title {
    padding-top: 1.25rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 1rem;
    font-size: 1.125rem;
    font-weight: 700;
  }

  .v-card__text {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 1.5rem;
    color: rgba($gray9, 0.8);
    font-size: 1rem;
  }

  // Contact Info
  .contact-info {
    margin-top: 1.5rem;
    padding: 0;
    font-weight: 500;
    list-style-type: none;
  }

  .contact-info__row {
    display: flex;
    align-items: flex-start;
  }

  .contact-info__type {
    flex: 0 0 auto;
    min-width: 4rem;
    overflow: hidden;
    letter-spacing: -0.02rem;
    font-weight: 700;
  }

  .contact-info__value {
    flex: 1 1 auto;
    overflow: hidden;
  }
</style>
