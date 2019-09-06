<template>
  <v-card class="support-info-card">
    <header>Need Assistance?</header>
    <div class="container">
      <p>For support or questions about this application, please contact us at:</p>
      <ul class="contact-list">
        <li class="contact-list__row">
          <v-icon small color="primary">phone</v-icon>
          <span class="contact-info__value">{{ $t('techSupportPhone') }}</span>
        </li>
        <li class="contact-list__row">
          <v-icon small color="primary">email</v-icon>
          <span class="contact-info__value"><a v-bind:href="'mailto:' + $t('techSupportEmail')">{{ $t('techSupportEmail') }}</a></span>
        </li>
      </ul>
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'SupportInfoCard'
}
</script>

<style lang="scss" scoped>
  @import "../assets/scss/theme.scss";

  .support-info-card{
    font-size: 1rem;
  }

  header{
    padding: 1.5rem;
    padding-bottom: 0;
    font-size: 1.5em;
    font-weight: 500;
  }

  .container{
    padding-top: 1.125rem;
    font-size: 1em;
  }

  @media (min-width: 960px){
    header{
      font-size: 1.125em;
    }

    .container{
      font-size: 0.875em
    }
  }

  .contact-list{
    margin-top: 1.5rem;
    padding: 0;
    font-weight: 500;
    list-style-type: none;
  }

  .contact-list__row{
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .contact-list__row .v-icon{
      vertical-align: middle;
      margin-top: -0.15rem;
      margin-right: 1rem;
  }

  .contact-list__row + .contact-list__row{
    margin-top: 0.2rem;
  }

</style>
