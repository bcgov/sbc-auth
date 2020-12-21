<template>
  <main class="view-container container">
      <h1 class="mb-4">Price List</h1>
      <p class="mb-8">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
      <section class="mb-10">
        <h2 class="mb-5">Business Registry</h2>
        <table tile>
          <thead>
            <th class="product text-left">Product</th>
            <th class="fee">Price</th>
            <th class="fee--service">Service Fee</th>
            <th class="fee--priority">Priority Fee</th>
            <th class="fee--future">Future Effective Fee</th>
          </thead>
          <tbody>
            <tr v-for="item in pricelist" :key="item.name">
              <td class="product font-weight-bold">{{item.name}}</td>
              <td class="fee">
                <span aria-describedby="Annual Report PRice">${{item.price}}</span>
              </td>
              <td class="fee--service">${{item.serviceFee}}</td>
              <td class="fee--priority">${{item.priorityFee}}</td>
              <td class="fee--future">${{item.futureEffectiveFee}}</td>
            </tr>
          </tbody>
        </table>
      </section>
      <section class="mb-10">
        <h2 class="mb-5">Personal Property Registry</h2>
        <table tile>
          <thead>
            <th class="product text-left">Product</th>
            <th class="fee">Price</th>
            <th class="fee--service">Service Fee</th>
            <th class="fee--priority">Priority Fee</th>
            <th class="fee--future">Future Effective Fee</th>
          </thead>
          <tbody>
            <tr v-for="item in pricelist" :key="item.name">
              <td class="product font-weight-bold">{{item.name}}</td>
              <td class="fee">
                <span aria-describedby="Annual Report PRice">${{item.price}}</span>
              </td>
              <td class="fee--service">${{item.serviceFee}}</td>
              <td class="fee--priority">${{item.priorityFee}}</td>
              <td class="fee--future">${{item.futureEffectiveFee}}</td>
            </tr>
          </tbody>
        </table>
      </section>
  </main>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { VueConstructor } from 'vue'

@Component({
  name: 'FeeScheduleView'
})

export default class FeeScheduleView extends Vue {
  data () {
    return {
      pricelist: [
        {
          name: 'Annual Report',
          price: '40.00',
          serviceFee: '1.50',
          priorityFee: '100.00',
          futureEffectiveFee: '100.00'
        },
        {
          name: 'Change of Registered Office Address',
          price: '20.00',
          serviceFee: '1.50',
          priorityFee: '100.00',
          futureEffectiveFee: '100.00'
        },
        {
          name: 'Change of Directors',
          price: '20.00',
          serviceFee: '1.50',
          priorityFee: '100.00',
          futureEffectiveFee: '100.00'
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
  main {
    margin: 0 auto;
  }

  table {
    width: 100%;
    background: #ffffff;
    border-top: 0;
    border-bottom: 0;
    border-collapse: collapse;
    font-size: 0.875rem;
    table-layout: fixed;
  }

  th, td {
    padding: 0.75rem;
    vertical-align: top;
    border-top: 1px solid var(--v-grey-base);
    border: 1px solid var(--v-grey-base);
  }

  th {
    font-size: 0.8125rem;
    font-weight: normal;
    text-align: left;
    white-space: nowrap;
  }

  td {
    padding: 0.75rem;
    vertical-align: top;
  }

  td.fee {
    font-weight: 700;
  }

  th[class^='fee'] {
    width: 200px;
  }

  th[class^='fee'],
  td[class^='fee'] {
    text-align: right;
  }

  .product {
    white-space: nowrap;
    overflow: hidden;
    background: #f7f8fa;
  }

  @media (max-width: 1024px) {
    thead {
      display: none;
    }

    table {
      border-collapse: collapse;
      border-width: 0 1px 1px 1px;
    }

    td {
      position: relative;
      width: 100%;
      display: flex;
      justify-content: space-between;
      border-width: 1px 0 0 0;
    }

    td.product {
      padding-top: 1rem;
      padding-bottom: 1rem;
    }

    td[class^='fee']::before {
      flex: 0 0 auto;
    }

    .fee::before {
      content: 'Price';
    }

    .fee--service::before {
      content: 'Service Fee';
    }

    .fee--priority::before {
      content: 'Priority';
    }

    .fee--future::before {
      content: 'Future Effective Date';
    }
  }
</style>
