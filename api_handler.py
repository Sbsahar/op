import requests
import json
from typing import Dict, Any, Optional

# إعدادات API
API_BASE_URL = "https://kd1s.com/api/v2"
API_KEY = "d7e9b9d035ac6b5032a78d9b4559a748"  # ضع مفتاحك هنا

def make_api_request(action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    إرسال طلب إلى KD Media API
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # دائماً نضيف key و action
    if params is None:
        params = {}
    
    params.update({
        'key': API_KEY,
        'action': action
    })
    
    try:
        print(f"🔄 إرسال طلب API: {action} مع المعاملات: {params}")
        
        response = requests.post(API_BASE_URL, data=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ رد الـ API: {result}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"خطأ في الاتصال بالـ API: {str(e)}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    
    except json.JSONDecodeError as e:
        error_msg = f"خطأ في تحليل JSON: {str(e)}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    
    except Exception as e:
        error_msg = f"خطأ غير متوقع: {str(e)}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}

def get_services() -> Dict[str, Any]:
    """
    جلب قائمة الخدمات من الـ API
    """
    return make_api_request('services')

def get_balance() -> Dict[str, Any]:
    """
    جلب رصيد الحساب
    """
    return make_api_request('balance')

def add_order(service_id: int, link: str, quantity: int, runs: Optional[int] = None, interval: Optional[int] = None) -> Dict[str, Any]:
    """
    إضافة طلب جديد
    """
    params = {
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    
    if runs:
        params['runs'] = runs
    if interval:
        params['interval'] = interval
    
    return make_api_request('add', params)

def get_order_status(order_id: int) -> Dict[str, Any]:
    """
    جلب حالة طلب واحد
    """
    params = {'order': order_id}
    return make_api_request('status', params)

def get_multiple_order_status(order_ids: str) -> Dict[str, Any]:
    """
    جلب حالة عدة طلبات
    """
    params = {'orders': order_ids}
    return make_api_request('status', params)

def create_refill(order_id: int) -> Dict[str, Any]:
    """
    طلب إعادة تعبئة
    """
    params = {'order': order_id}
    return make_api_request('refill', params)

def get_refill_status(refill_id: int) -> Dict[str, Any]:
    """
    جلب حالة إعادة التعبئة
    """
    params = {'refill': refill_id}
    return make_api_request('refill_status', params)

def cancel_order(order_id: int) -> Dict[str, Any]:
    """
    إلغاء طلب
    """
    params = {'orders': str(order_id)}
    return make_api_request('cancel', params)

# اختبار الاتصال
def test_api_connection() -> bool:
    """
    اختبار الاتصال بالـ API
    """
    balance_response = get_balance()
    if 'error' not in balance_response:
        print(f"✅ الاتصال ناجح - الرصيد: {balance_response}")
        return True
    else:
        print(f"❌ فشل الاتصال: {balance_response}")
        return False

# تشغيل اختبار عند بدء الملف
if __name__ == "__main__":
    print("🧪 اختبار الاتصال بـ KD Media API...")
    if test_api_connection():
        print("✅ الـ API يعمل بشكل صحيح!")
        
        # اختبار جلب الخدمات
        services = get_services()
        if 'error' not in services:
            print(f"✅ تم جلب {len(services)} خدمة بنجاح")
            print("مثال على أول خدمة:", services[0] if services else "لا توجد خدمات")
        else:
            print(f"❌ خطأ في جلب الخدمات: {services}")
    else:
        print("❌ المفتاح غير صحيح أو مشكلة في الاتصال")
