import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO
from supabase import create_client  # <--- 이 부분이 누락되면 supabase 에러가 납니다.

# 1. 초기 설정 및 DB 연결 (가장 중요!)
# Streamlit Cloud의 Settings > Secrets에 아래 값이 들어있어야 합니다.
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Supabase 연결 정보를 설정해주세요. (Secrets 확인 필요)")
    st.stop() # 설정 안 되어 있으면 아래 코드 실행 중단

st.title("🔥 산불 방재 데이터베이스 통합 관리 시스템")

# 2. 과제 요구사항: 실시간 DB 연동 현황 출력
st.divider()
st.subheader("📋 실시간 데이터베이스 연동 현황")

try:
    # DB에서 메타데이터 가져오기
    response = supabase.table("map_metadata").select("*").execute()
    
    if response.data:
        meta = response.data[0]
        
        # 1. 텍스트 정보 출력
        col1, col2 = st.columns(2)
        col1.success(f"📍 연동 지역: {meta['region_name']}")
        col2.info(f"📏 격자 해상도: {meta['grid_size_m']}m")
        
        # 2. 파일 다운로드 테스트 버튼 (데이터 정합성 확인용)
        if st.button("파일 다운로드 테스트 및 데이터 시각화"):
            with st.spinner("Storage에서 데이터를 불러오는 중..."):
                # 각 Storage URL에서 데이터 가져오기
                dem_res = requests.get(meta['dem_file_url'])
                road_res = requests.get(meta['road_file_url'])
                
                if dem_res.status_code == 200 and road_res.status_code == 200:
                    # 메모리에서 바로 npy 읽기
                    test_dem = np.load(BytesIO(dem_res.content))
                    test_road = np.load(BytesIO(road_res.content))
                    
                    st.write(f"✅ 지형 데이터 로드 성공: {test_dem.shape}")
                    st.write(f"✅ 임도 데이터 로드 성공: {test_road.shape}")
                    
                    # 3. 간단한 시각화 (데이터가 잘 들어왔는지 확인)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        # 고도 데이터 정규화 시각화
                        normalized_dem = (test_dem - np.min(test_dem)) / (np.max(test_dem) - np.min(test_dem))
                        st.image(normalized_dem, caption="고도(DEM) 데이터", use_column_width=True)
                    with col_b:
                        # 임도 데이터 시각화
                        st.image(test_road.astype(float), caption="임도(Road) 데이터", use_column_width=True)
                else:
                    st.error("Storage URL에서 파일을 가져오지 못했습니다. Public 설정을 확인하세요.")
    else:
        st.warning("데이터베이스에 등록된 시나리오가 없습니다.")

except Exception as e:
    st.error(f"⚠️ 시스템 오류 발생: {e}")

# 4. DB 테이블 전체 보기 (과제 증빙용)
st.divider()
if st.checkbox("DB 테이블 원본 데이터 보기"):
    st.write("`map_metadata` 테이블 상세")
    st.dataframe(pd.DataFrame(response.data))
