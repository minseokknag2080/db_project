import numpy as np
import requests
from io import BytesIO

# --- (기존 코드 생략) ---

st.divider()
st.subheader("📋 실시간 데이터베이스 연동 현황")

# DB에서 메타데이터 가져오기
try:
    response = supabase.table("map_metadata").select("*").execute()
    if response.data:
        meta = response.data[0]
        
        # 1. 텍스트 정보 출력
        col1, col2 = st.columns(2)
        col1.success(f"연동 지역: {meta['region_name']}")
        col2.info(f"격자 해상도: {meta['grid_size_m']}m")
        
        # 2. 파일 다운로드 테스트 버튼 (과제 확인용)
        if st.button("파일 다운로드 테스트 및 데이터 확인"):
            # 지형 데이터 URL 시식
            dem_res = requests.get(meta['dem_file_url'])
            road_res = requests.get(meta['road_file_url'])
            
            if dem_res.status_code == 200:
                # 메모리에서 바로 npy 읽기
                test_dem = np.load(BytesIO(dem_res.content))
                test_road = np.load(BytesIO(road_res.content))
                
                st.write(f"✅ 지형 데이터 로드 성공: {test_dem.shape}")
                st.write(f"✅ 임도 데이터 로드 성공: {test_road.shape}")
                
                # 간단한 시각화 추가 (잘 되었는지 확인용)
                st.image(test_dem / np.max(test_dem), caption="고도 데이터 시각화", width=300)
    else:
        st.warning("데이터베이스에 등록된 시나리오가 없습니다.")
except Exception as e:
    st.error(f"DB 조회 중 오류 발생: {e}")
