<template>
  <div class="view-container">
    <article>
      <h1 class="mb-3">File Annual Reports Online</h1>
      <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
      <section class="mt-4">
        <h2 class="mb-2">Sign in to your account</h2>
        <p style="margin-bottom: 2rem">Once you have received your <strong>Annual Report Filing Notice</strong> Letter you will be able to file start filing online. If you haven't yet received your letter, please contact BC Registries toll-free at 1-800-663-6102 (Mon-Fri, 8am-7pm).</p>
        <PasscodeForm/>
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

  .view-container
    display flex
    flex-flow column nowrap

  article
    flex 1 1 auto

  aside
    flex 0 0 auto
    margin-top 2rem

  @media (min-width: 960px)
    .view-container
        flex-flow row nowrap

    aside
      margin-top 0
      margin-left 2rem
      width 20rem

</style>