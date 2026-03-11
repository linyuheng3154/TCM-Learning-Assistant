"""
API接口测试 - API Endpoint Tests

本模块测试FastAPI接口的功能和扩展字段支持。

AI协作说明：
- 测试确保API接口正确处理各种请求
- 验证扩展字段查询功能的正确性
- 确保错误处理和状态码正确
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


# 创建测试客户端
client = TestClient(app)


class TestBasicAPI:
    """测试基础API接口"""
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "TCM Learning Assistant API" in data["message"]
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestFormulasAPI:
    """测试方剂API接口"""
    
    def test_get_all_formulas(self):
        """测试获取所有方剂列表"""
        response = client.get("/formulas/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # 检查返回数据的基本结构
        if len(data) > 0:
            formula = data[0]
            assert "id" in formula
            assert "name" in formula
            assert "efficacy" in formula
    
    def test_get_formula_by_id(self):
        """测试根据ID获取方剂详情"""
        response = client.get("/formulas/f001")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == "f001"
            assert "name" in data
            assert "composition" in data
            assert isinstance(data["composition"], list)
        elif response.status_code == 404:
            # 如果f001不存在，测试其他存在的ID
            all_response = client.get("/formulas/")
            if all_response.status_code == 200 and len(all_response.json()) > 0:
                test_id = all_response.json()[0]["id"]
                response = client.get(f"/formulas/{test_id}")
                assert response.status_code == 200
    
    def test_search_formulas(self):
        """测试搜索方剂"""
        response = client.get("/formulas/search?keyword=桂枝")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # 检查搜索结果结构
        if len(data) > 0:
            result = data[0]
            assert "formula" in result
            assert "score" in result
            assert "matched_fields" in result
    
    def test_search_with_empty_keyword(self):
        """测试空关键词搜索"""
        response = client.get("/formulas/search?keyword=")
        assert response.status_code == 422  # 验证错误


class TestExtendedAPI:
    """测试扩展API接口"""
    
    def test_get_expanded_formula(self):
        """测试获取扩展方剂信息"""
        response = client.get("/formulas/expanded/f001")
        
        if response.status_code == 200:
            data = response.json()
            # 检查扩展字段
            assert "alias" in data
            assert "modern_research" in data
            assert "clinical_cases" in data
            assert isinstance(data["alias"], list)
            assert isinstance(data["clinical_cases"], list)
        elif response.status_code == 404:
            # 如果f001不存在，测试其他存在的ID
            all_response = client.get("/formulas/")
            if all_response.status_code == 200 and len(all_response.json()) > 0:
                test_id = all_response.json()[0]["id"]
                response = client.get(f"/formulas/expanded/{test_id}")
                if response.status_code == 200:
                    data = response.json()
                    assert "alias" in data
                    assert "modern_research" in data
    
    def test_advanced_search(self):
        """测试高级搜索"""
        response = client.get("/formulas/search/advanced?keyword=桂枝")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_advanced_search_with_filters(self):
        """测试带过滤器的高级搜索"""
        response = client.get(
            "/formulas/search/advanced?keyword=桂枝&category=解表剂"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_categories_list(self):
        """测试获取分类列表"""
        response = client.get("/formulas/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # 检查分类数据
        if len(data) > 0:
            assert isinstance(data[0], str)


class TestErrorHandling:
    """测试错误处理"""
    
    def test_nonexistent_formula(self):
        """测试不存在的方剂"""
        response = client.get("/formulas/f999")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_invalid_formula_id_format(self):
        """测试无效的方剂ID格式"""
        response = client.get("/formulas/invalid_id")
        # 可能返回404或400，取决于具体实现
        assert response.status_code in [400, 404]


class TestMetadataAPI:
    """测试元数据API"""
    
    def test_get_metadata(self):
        """测试获取元数据"""
        response = client.get("/formulas/metadata/info")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        
        # 检查元数据字段
        if "total_formulas" in data:
            assert isinstance(data["total_formulas"], int)
        if "source" in data:
            assert isinstance(data["source"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])