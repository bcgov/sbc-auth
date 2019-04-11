<template>
  <div class="view-container">
    <article>
      <h1>File Annual Reports Online</h1>
      <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
      <section>
        <h2>Get Started...</h2>
        <p>Once you have received your <strong>Passcode Notice Letter</strong> you will be able to file start filing online. If you haven't yet received your letter, please contact BC Registries toll-free at 1-800-663-6102 (Monday to Friday, 8am-7pm).</p>
      </section>
      <section>
        <v-card>
          <v-container class="passcode-container">
            <h3>Sign In</h3>
            <PasscodeForm/>
          </v-container>
        </v-card>
      </section>
    </article>
    <aside>
      <SupportInfoCard/>
    </aside>
  </div>
</template>

<script>
import Vue from 'vue';
import PasscodeForm from '@/components/PasscodeForm.vue';
import SupportInfoCard from '@/components/SupportInfoCard.vue';

export default ({
  name: 'Home',
  components: {
    PasscodeForm,
    SupportInfoCard
  }
});
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  h1
    margin-bottom 1rem
    letter-spacing -0.02rem

  h2
    margin-bottom 0.75rem
    letter-spacing -0.02rem

  h3
    margin-bottom 1.5rem

  section
    margin-top 2rem

  .view-container
    display flex
    flex-flow column nowrap

  article
    flex 1 1 auto

  aside
    flex 0 0 auto
    margin-top 3rem

  @media (min-width: 960px)
    .view-container
        flex-flow row nowrap

    aside
      margin-top 0
      margin-left 2rem
      width 20rem

    .passcode-container
      padding 2rem

</style>