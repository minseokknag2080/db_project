import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO
from supabase import create_client

# 1. 초기 설정 및 DB 연결
# 이 부분에서 에러가 나면 아래 코드가 실행되지 않도록 안전장치를 강화했습니다.
supabase = None
response = None

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Supabase 연결 정보를 설정해주세요: {e}")
    st.stop()

st.title("🔥 산불 방재 데이터베이스 통합 관리 시스템")

# 2. 실시간 DB 연동 현황 출력
st.divider()
st.subheader("📋 실시간 데이터베이스 연동 현황")

try:
    # 📍 중요: 테이블 이름을 명시적으로 확인하세요. 
    # 만약 Supabase Table Editor에 이름이 대문자라면 대문자로 바꿔야 합니다.
    response = supabase.table("map_metadata").select("*").execute()
    
    if response and hasattr(response, 'data') and response.data:
        meta = response.data[0]
        
        # URL 클리닝 (공백, 따옴표 제거)
        dem_url = str(meta['dem_file_url']).strip().replace('"', '').replace("'", "")
        road_url = str(meta['road_file_url']).strip().replace('"', '').replace("'", "")
        
        # 1. 텍스트 정보 출력
        col1, col2 = st.columns(2)
        col1.success(f"📍 연동 지역: {meta.get('region_name', '알 수 없음')}")
        col2.info(f"📏 격자 해상도: {meta.get('grid_size_m', 0)}m")
        
        # 2. 파일 다운로드 테스트 버튼
        if st.button("파일 다운로드 테스트 및 데이터 시각화"):
            with st.spinner("Storage에서 데이터를 불러오는 중..."):
                dem_res = requests.get(dem_url)
                road_res = requests.get(road_url)
                
                if dem_res.status_code == 200 and road_res.status_code == 200:
                    test_dem = np.load(BytesIO(dem_res.content))
                    test_road = np.load(BytesIO(road_res.content))
                    
                    st.write(f"✅ 지형 데이터 로드 성공: {test_dem.shape}")
                    st.write(f"✅ 임도 데이터 로드 성공: {test_road.shape}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        # 0으로 나누기 방지 추가
                        dem_range = np.max(test_dem) - np.min(test_dem)
                        normalized_dem = (test_dem - np.min(test_dem)) / dem_range if dem_range != 0 else test_dem
                        st.image(normalized_dem, caption="고도(DEM) 데이터", use_column_width=True)
                    with col_b:
                        st.image(test_road.astype(float), caption="임도(Road) 데이터", use_column_width=True)
                else:
                    st.error(f"⚠️ Storage 연결 실패 (Status: {dem_res.status_code})")
                    st.write(f"확인된 URL: `{dem_url}`")
    else:
        st.warning("데이터베이스에 등록된 시나리오가 없거나 데이터를 불러올 수 없습니다.")

except Exception as e:
    st.error(f"⚠️ 시스템 오류 발생: {e}")
    st.info("Tip: Supabase Table Editor에서 테이블 이름이 'map_metadata'가 맞는지, 소문자인지 확인해주세요.")

# 3. DB 테이블 전체 보기 (NameError 방지 로직 추가)
st.divider()
if st.checkbox("DB 테이블 원본 데이터 보기"):
    st.write("`map_metadata` 테이블 상세")
    # response가 성공적으로 생성되었을 때만 데이터프레임 출력
    if response and hasattr(response, 'data'):
        st.dataframe(pd.DataFrame(response.data))
    else:
        st.error("데이터를 불러오지 못해 테이블을 표시할 수 없습니다.")
