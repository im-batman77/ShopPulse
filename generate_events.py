import pandas as pd
import numpy as np
import uuid
from datetime import timedelta

def generate_events():
    print("Loading orders dataset...")
    try:
        orders = pd.read_csv("data/olist_orders_dataset.csv")
    except Exception as e:
        print(f"Error loading orders: {e}")
        return
        
    orders = orders[orders['order_status'] == 'delivered'].copy()
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    
    events = []
    assignments = []
    
    # 1. Generate events for people who purchased
    print("Generating events for actual buyers...")
    np.random.seed(42)
    buyer_customer_ids = orders['customer_id'].unique()
    
    for _, row in orders.iterrows(): 
        cid = row['customer_id']
        pur_time = row['order_purchase_timestamp']
        
        # A/B test assignment (50/50 split)
        group = np.random.choice(['control', 'treatment'])
        assignments.append({'customer_id': cid, 'test_group': group})
        
        # Funnel events leading to purchase
        events.append({'customer_id': cid, 'event_type': 'page_view', 'event_time': pur_time - timedelta(minutes=np.random.randint(20, 60))})
        events.append({'customer_id': cid, 'event_type': 'add_to_cart', 'event_time': pur_time - timedelta(minutes=np.random.randint(10, 20))})
        events.append({'customer_id': cid, 'event_type': 'checkout', 'event_time': pur_time - timedelta(minutes=np.random.randint(2, 10))})
        events.append({'customer_id': cid, 'event_type': 'purchase', 'event_time': pur_time})

    # 2. Generate events for people who dropped off
    print("Generating drop-off events...")
    # Generate fake non-buyer customer IDs
    num_buyers = len(buyer_customer_ids)
    # Funnel: 100k page views -> 60k add to cart -> 30k checkout -> ~96k actual buyers? Wait, Olist has ~96k delivered orders.
    # Let's say: 300k page_views -> 150k add_to_cart -> 110k checkout -> 96k buyers.
    num_drop_page_view = 150000
    num_drop_add_to_cart = 50000
    num_drop_checkout = 15000
    
    def generate_dropoffs(num_users, last_step, start_time_range):
        nonlocal events, assignments
        fake_cids = [uuid.uuid4().hex for _ in range(num_users)]
        
        # assign groups
        for cid in fake_cids:
            # Treatment has higher conversion, so drop-off should be skewed slightly towards control at checkout
            if last_step == 'checkout':
                # Control drops off more at checkout
                group = np.random.choice(['control', 'treatment'], p=[0.55, 0.45])
            else:
                group = np.random.choice(['control', 'treatment'])
            
            assignments.append({'customer_id': cid, 'test_group': group})
            
            base_time = pd.Timestamp("2018-01-01") + pd.to_timedelta(np.random.randint(0, 365), unit='D')
            
            events.append({'customer_id': cid, 'event_type': 'page_view', 'event_time': base_time})
            if last_step in ['add_to_cart', 'checkout']:
                events.append({'customer_id': cid, 'event_type': 'add_to_cart', 'event_time': base_time + timedelta(minutes=np.random.randint(2, 10))})
            if last_step == 'checkout':
                events.append({'customer_id': cid, 'event_type': 'checkout', 'event_time': base_time + timedelta(minutes=np.random.randint(12, 20))})

    generate_dropoffs(num_drop_page_view, 'page_view', None)
    generate_dropoffs(num_drop_add_to_cart, 'add_to_cart', None)
    generate_dropoffs(num_drop_checkout, 'checkout', None)
    
    print("Saving to CSV...")
    events_df = pd.DataFrame(events)
    events_df.to_csv("data/website_events.csv", index=False)
    
    assign_df = pd.DataFrame(assignments)
    assign_df.to_csv("data/ab_test_assignments.csv", index=False)
    print("Done! Generated {} events and {} assignments.".format(len(events_df), len(assign_df)))

if __name__ == "__main__":
    generate_events()
