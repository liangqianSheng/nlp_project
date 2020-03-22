<template>
<div>
  <div class="title">请输入一段文本：</div>
<el-input
  type="text"
  placeholder="请输入标题"
  maxlength="50"
  class="title-input"
  v-model="title">
    <template slot="prepend">标题</template>

</el-input>
   <el-input
  type="textarea"
  :autosize="{ minRows: 6, maxRows: 12}"
  placeholder="请输入文本内容"
  maxlength="2000"
  show-word-limit
  v-model="content">
  <template slot="prepend">文本</template>
</el-input>
<div class="button-wrap">
  <el-button v-show="status !== STATUS.PROCESS" @click="handleAnaly" type="primary" plain>开始分析</el-button>
  <!-- <el-button v-show="status !== STATUS.PROCESS" @click="test" type="primary" plain>开始分析get</el-button> -->
  <!-- <el-button v-show="status !== STATUS.PROCESS" @click="testPost" type="primary" plain>开始分析post</el-button> -->
</div>
<div class="process" v-show="status === STATUS.PROCESS">
  <el-progress type="line" :percentage="percent" text-inside
  :stroke-width="30"
  show-text
  ></el-progress>
  <center>分析中...</center>
</div>
<!-- v-show="status === STATUS.completed"  -->
<div v-show="status === STATUS.COMPLET" class="result">
  <div class="result-title">自动摘要结果</div>
  <div class="result-content">
  {{result}}
  </div>
</div>
</div>
</template>

<script>
import axios from 'axios'
const STATUS = {
  READY: 0,
  PROCESS: 1,
  COMPLET: 2
}
export default {
  data () {
    return {
      title: '',
      content: '',
      result: '',
      status: STATUS.READY,
      percent: 0,
      completed: false,
      STATUS: STATUS

    }
  },
  methods: {
    async handleAnaly () {
      if (!this.title) {
        return this.$message.error('请输入标题')
      }
      if (!this.content) {
        return this.$message.error('请输入内容')
      }
      this.timeStep = 200

      this.timer = () => setTimeout(() => {
        if (this.percent >= 99) {
          clearTimeout(this.timer)
          return
        }
        this.percent = this.percent + 1
        if (this.percent > 30) {
          this.timeStep = 250
        }
        if (this.percent > 50) {
          this.timeStep = 300
        }
        if (this.percent < 95) {
          this.timer()
        }
      }, this.timeStep)
      this.timer()

      this.status = STATUS.PROCESS
      // const res = await axios.post('//localhost:8080', {
      //   content: this.content,
      //   title: this.title
      // })
      try {
        const hostname = process.env.NODE_ENV === 'production' ? 'xiangjiejie.qicp.vip' : 'xiangjiejie.qicp.vip'
        // const hostname = process.env.NODE_ENV === 'production' ? '0.0.0.0' : location.hostname
        console.log('process.env.NODE_ENV: ', process.env.NODE_ENV)
        const url = `http://${hostname}/index`
        console.log('url: ', url)
        const res = await axios.get(url, {
          params: {
            content: this.content,
            title: this.title
          }
        })
        if (res.data.code === 1) {
          this.result = res.data.data
          this.status = STATUS.COMPLET
        } else {
          this.$message.error(res.data.message)
          this.status = STATUS.READY
        }
      } catch (e) {
        this.$message.error(JSON.stringify(e.stack))
        this.status = STATUS.READY
      }
    }
    // async test () {
    //   const res = await axios.get('//localhost:8080/index', {
    //     params: {
    //       content: this.content,
    //       title: this.title
    //     }
    //   })
    // },
    // async testPost () {
    //   const res = await axios.post('//localhost:8080/index', {
    //     content: this.content,
    //     title: this.title
    //   })
    // }
  }
}
</script>

<style  scoped>
.title{
  font-weight: 600;
  padding: 20px 0;
}
.title-input{
  margin-bottom: 15px;
}
.button-wrap{
  margin: 50px 0;
  text-align: center;
}

.result{
  padding: 0 10px;
  border-radius: 4px;
  border:1px solid #dcdfe6;
}
.result-title{
  padding: 10px 0;
  font-weight: 600;
  border-bottom: 1px solid #dcdfe6;
}
.result-content{
  padding: 10px 0;
}
.process{
  width:500px;
  margin: 0 auto 50px auto;
}

</style>
