import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

st.title('日本の賃金データダッシュボード')

df_jp_ind      = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv',     encoding='shift_jis')
df_jp_category = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv',     encoding='shift_jis')
df_pref_ind    = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv',  encoding='shift_jis')

#########################################
# ■2019年：一人当たり平均賃金のヒートマップ
#########################################
st.header('■2019年：一人当たり平均賃金のヒートマップ')

# 各都道府県の緯度・軽度データを取得
jap_lat_lon = pd.read_csv('./pref_lat_lon.csv')
jap_lat_lon = jap_lat_lon.rename(columns={'pref_name': '都道府県名'})

# 2019年度の都道府県別・年齢別の賃金データを取得
df_pref_map = df_pref_ind[(df_pref_ind['年齢'] == '年齢計') & (df_pref_ind['集計年'] == 2019)]

# 緯度・軽度データと賃金データを結合
df_pref_map = pd.merge(df_pref_map, jap_lat_lon, on='都道府県名')

# 正規化した一人当たり賃金をセット
df_pref_map['一人当たり賃金（相対値）'] = ((df_pref_map['一人当たり賃金（万円）'] - df_pref_map['一人当たり賃金（万円）'].min()) / (df_pref_map['一人当たり賃金（万円）'].max() - df_pref_map['一人当たり賃金（万円）'].min()))

# ヒートマップの各種設定
# View
view = pdk.ViewState(
     longitude=139.691648
    ,latitude=35.689185
    ,zoom=4
    ,pitch=40.5
)
# Layer
layer = pdk.Layer(
     'HeatmapLayer'
    ,data=df_pref_map
    ,opacity=0.4
    ,get_position=['lon', 'lat']
    ,threshold=0.3
    ,get_weight= '一人当たり賃金（相対値）'
)
# Deck
layer_map = pdk.Deck(
     layers = layer
    ,initial_view_state=view
)

# ヒートマップの描画
st.pydeck_chart(layer_map)

show_df = st.checkbox('Show DataFrame')

if show_df == True:
    st.write(df_pref_map)

#########################################
# ■集計年別の一人当たり賃金（万円）の推移：折れ線グラフ
#########################################
st.header('■集計年別の一人当たり賃金（万円）の推移')

# 集計年別の全国賃金データを取得
df_ts_mean = df_jp_ind[(df_jp_ind['年齢'] == '年齢計')]
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）': '全国_一人当たり賃金（万円）'})

# 集計年別の都道府県別賃金データを取得（セレクトボックスで都道府県を選択可能）
df_pref_mean = df_pref_ind[(df_pref_ind['年齢'] == '年齢計')]
pref_list    = df_pref_mean['都道府県名'].unique()
option_pref  = st.selectbox('都道府県名', pref_list)

df_pref_mean = df_pref_mean[df_pref_mean['都道府県名'] == option_pref]

# 全国データと都道府県別データを結合
df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on='集計年')
df_mean_line = df_mean_line[['集計年', '全国_一人当たり賃金（万円）', '一人当たり賃金（万円）']]
df_mean_line = df_mean_line.set_index('集計年')

# 折れ線グラフの描画
st.line_chart(df_mean_line)


#########################################
# ■年齢階級別の全国一人あたり平均賃金（万円）：バブルチャート
#########################################
st.header('■年齢階級別の全国一人あたり平均賃金（万円）')

# 年齢階級別の全国賃金データを取得
df_mean_bubble = df_jp_ind[(df_jp_ind['年齢'] != '年齢計')]

# バブルチャートの設定
fig = px.scatter(
     df_mean_bubble
    ,x='一人当たり賃金（万円）'
    ,y='年間賞与その他特別給与額（万円）'
    ,range_x=[150,700]
    ,range_y=[0,150]
    ,size='所定内給与額（万円）'
    ,size_max=38
    ,color='年齢'
    ,animation_frame='集計年'
    ,animation_group='年齢'
)

#バブルチャートの描画
st.plotly_chart(fig)


#########################################
# ■産業別の賃金推移：横棒グラフ
#########################################
st.header('■産業別の賃金推移')

year_list   = df_jp_category['集計年'].unique()
option_year = st.selectbox('集計年', year_list)

wage_list   = ['一人当たり賃金（万円）', '所定内給与額（万円）', '年間賞与その他特別給与額（万円）']
option_wage = st.selectbox('賃金の種類', wage_list)

df_mean_category = df_jp_category[df_jp_category['集計年'] == option_year]
max_x = df_mean_category[option_wage].max() + 50

# 棒グラフの設定
fig = px.bar(
     df_mean_category
    ,x=option_wage
    ,y='産業大分類名'
    ,color='産業大分類名'
    ,animation_frame='年齢'
    ,range_x=[0,max_x]
    ,orientation='h'
    ,width=800
    ,height=500
)

# 棒グラフの描画
st.plotly_chart(fig)

# ※データの出典元は必ず記載すること
st.text('出典：RESAS（地域経済分析システム）')
st.text('本結果はRESAS（地域経済分析システム）を加工して作成')