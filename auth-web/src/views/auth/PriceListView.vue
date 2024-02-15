<template>
  <main class="view-container container">
    <h1 class="mb-4">
      Price List
    </h1>
    <p class="mb-8">
      Where applicable, tax is included in the price shown. Prices are subject to change without notice.
    </p>
    <section class="mb-10">
      <h2 class="mb-5">
        Business Registry
      </h2>
      <h3 class="mt-8 mb-6">
        Cooperative Associations
      </h3>
      <v-card flat>
        <table aria-label="Price List Table">
          <thead>
            <th
              class="product text-left"
              scope="col"
            >
              Product
            </th>
            <th
              class="fee"
              scope="col"
            >
              Price
            </th>
            <th
              class="fee--service"
              scope="col"
            >
              Service Fee
            </th>
            <th
              class="fee--future"
              scope="col"
            >
              Future Effective Fee
            </th>
          </thead>
          <tbody>
            <tr
              v-for="item in coopPriceList"
              :key="item.name"
            >
              <td
                class="product font-weight-bold"
              >
                {{ item.name }}
              </td>
              <td
                class="fee"
              >
                <span aria-describedby="Annual Report PRice">{{ '$' + item.price }}</span>
              </td>
              <td
                class="fee--service"
              >
                <span v-if="item.serviceFee">{{ '$' + item.serviceFee }}</span>
              </td>
              <td
                class="fee--future"
              >
                <span v-if="item.futureEffectiveFee">{{ '$' + item.futureEffectiveFee }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </v-card>
      <h3 class="mt-8 mb-6">
        Benefit Companies
      </h3>
      <v-card flat>
        <table aria-label="Price List Table">
          <thead>
            <th
              class="product text-left"
              scope="col"
            >
              Product
            </th>
            <th
              class="fee"
              scope="col"
            >
              Price
            </th>
            <th
              class="fee--service"
              scope="col"
            >
              Service Fee
            </th>
            <th
              class="fee--future"
              scope="col"
            >
              Future Effective Fee
            </th>
          </thead>
          <tbody>
            <tr
              v-for="item in benefitCompanyPriceList"
              :key="item.name"
            >
              <td
                class="product font-weight-bold"
              >
                {{ item.name }}
              </td>
              <td
                class="fee"
              >
                <span aria-describedby="Annual Report PRice">{{ '$' + item.price }}</span>
              </td>
              <td
                class="fee--service"
              >
                <span v-if="item.serviceFee">{{ '$' + item.serviceFee }}</span>
              </td>
              <td
                class="fee--future"
              >
                <span v-if="item.futureEffectiveFee">{{ '$' + item.futureEffectiveFee }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </v-card>
    </section>
  </main>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'PriceListView',
  setup () {
    const priceList = [
      {
        businessType: 'cooperative',
        name: 'Annual Report',
        price: '30.00',
        serviceFee: '',
        futureEffectiveFee: ''
      },
      {
        businessType: 'cooperative',
        name: 'Correction',
        price: '20.00',
        serviceFee: '',
        futureEffectiveFee: ''
      },
      {
        businessType: 'cooperative',
        name: 'Change of Address',
        price: '20.00',
        serviceFee: '',
        futureEffectiveFee: ''
      },
      {
        businessType: 'cooperative',
        name: 'Change of Directors',
        price: '20.00',
        serviceFee: '',
        futureEffectiveFee: ''
      },
      {
        businessType: 'benefitCompany',
        name: 'Incorporation',
        price: '350.00',
        serviceFee: '1.50',
        futureEffectiveFee: '100.00'
      }
    ]

    const coopPriceList = priceList.filter((item) => {
      return (item.businessType === 'cooperative')
    })

    const benefitCompanyPriceList = priceList.filter((item) => {
      return (item.businessType === 'benefitCompany')
    })

    return {
      coopPriceList,
      benefitCompanyPriceList
    }
  }
})
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
    table-layout: fixed;
  }

  th, td {
    padding: 1rem;
    vertical-align: top;
    border-top: 1px solid var(--v-grey-lighten1);
    border: 1px solid var(--v-grey-lighten1);
  }

  th {
    font-weight: normal;
    text-align: left;
    white-space: nowrap;
  }

  td {
    padding: 1rem;
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
      border-width: 1px;
    }

    td {
      position: relative;
      margin-top: -1px;
      width: 100%;
      display: flex;
      justify-content: space-between;
      border-width: 1px;
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

    .fee--future::before {
      content: 'Future Effective Date';
    }
  }
</style>
